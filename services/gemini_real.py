# services/gemini_real.py
"""
Real Gemini client for Vision + Text using Google Generative AI.

Notes:
- Requires `google-generative-ai` package (pip install google-generative-ai).
- Expects environment variable GEMINI_API_KEY to be present in non-test mode.
- For Cloud Run we configured the secret and service account access; the secret is exposed
  to the container as the env var GEMINI_API_KEY (via --set-secrets in deployment).
- This implementation uses the google.generativeai client. If your environment
  requires a different auth flow, adapt accordingly (ADC / service account).
"""

import os
import time
import json
from typing import Dict, Any, Optional

# Try import; if missing, raise helpful error
try:
    import google.generativeai as genai
except Exception as e:
    raise RuntimeError("Please install google-generative-ai (pip install google-generative-ai)") from e

# Defaults - choose models per our hybrid decision
DEFAULT_VISION_MODEL = os.getenv("VISION_MODEL", "gemini-2.0-flash")
DEFAULT_TEXT_MODEL = os.getenv("TEXT_MODEL", "gemini-2.0-pro")

def _init_client_from_env():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY env var not set (required for real Gemini calls).")
    # genai accepts api_key configuration
    genai.configure(api_key=key)

def analyze_text_real(text: str, model: str = None) -> Dict[str, Any]:
    model = model or DEFAULT_TEXT_MODEL
    start = time.time()
    # strict JSON output prompt — ensure your analysis prompt is compatible
    prompt = (
        "You are a text-analysis assistant. Given the customer review contained between triple backticks, "
        "produce a single valid JSON object with the following fields:\n"
        "  - text: cleaned review text (string)\n"
        "  - sentiment: one of [\"positive\", \"neutral\", \"negative\", \"mixed\"]\n"
        "  - score: sentiment score between -1.0 and 1.0\n"
        "  - themes: array of short theme strings - top 3\n"
        "  - intent: one of [\"complaint\",\"praise\",\"feature_request\",\"question\",\"other\"]\n"
        "  - action_items: array of 0-3 suggested action items (strings)\n"
        "  - confidence: number between 0.0 and 1.0\n"
        "Return ONLY valid JSON (no surrounding text). Use temperature 0 for deterministic output.\n\n"
        f"```{text}```\n"
    )

    # Make sure client is configured
    _init_client_from_env()

    # Call the text model
    response = genai.generate_text(model=model, prompt=prompt, temperature=0.0, max_output_tokens=1024)
    raw = response.text or ""
    latency = int((time.time() - start) * 1000)

    # Attempt to parse JSON from the response (robustly)
    parsed = None
    try:
        # The model should return strict JSON; try to parse directly.
        parsed = json.loads(raw)
    except Exception:
        # Try to extract first JSON-looking substring
        import re
        m = re.search(r'(\{.*\})', raw, flags=re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(1))
            except Exception:
                parsed = None

    if parsed is None:
        # As a fallback, return a minimal structure noting failure
        return {
            "extracted_text": text,
            "analysis": {
                "sentiment": "neutral",
                "score": 0.0,
                "themes": [],
                "intent": "other",
                "action_items": [],
                "confidence": 0.0,
                "raw_text": raw[:1000]
            },
            "model": model,
            "processing_latency_ms": latency
        }

    # Normalize fields and types
    analysis = {
        "sentiment": parsed.get("sentiment"),
        "score": float(parsed.get("score")) if parsed.get("score") is not None else None,
        "themes": parsed.get("themes") or [],
        "intent": parsed.get("intent"),
        "action_items": parsed.get("action_items") or [],
        "confidence": float(parsed.get("confidence")) if parsed.get("confidence") is not None else None
    }

    return {
        "extracted_text": parsed.get("text") or text,
        "analysis": analysis,
        "model": model,
        "processing_latency_ms": latency,
    }

def analyze_image_real(image_bytes: bytes, model: Optional[str] = None) -> Dict[str, Any]:
    """
    For Vision, we send binary image to the multimodal generate endpoint.
    The google.generativeai client supports input image bytes; use generate_image_labeling/vision features.
    This is a best-effort example — if the library API differs, adapt accordingly.
    """
    model = model or DEFAULT_VISION_MODEL
    start = time.time()
    _init_client_from_env()

    # The API offers multimodal generate; here we ask the model to extract the review text only.
    # We use the "predict" style for multimodal: pass image bytes and short instruction.
    instruction = (
        "Extract only the customer review text visible in this screenshot. "
        "Return JSON: {\"extracted_text\":\"...\"}. Preserve emojis and punctuation. "
        "Do not add any commentary."
    )

    # Create an example request using the images param
    try:
        response = genai.generate_text(
            model=model,
            # supply both instruction and an image
            # different versions of the library use different param names; this is the recommended pattern
            prompt=instruction,
            images=[{"image_bytes": image_bytes}],
            temperature=0.0,
            max_output_tokens=512
        )
        raw = response.text or ""
    except Exception as e:
        # If the library does not support images that way, use a fallback prompt or raise
        return {
            "extracted_text": "",
            "analysis": {
                "sentiment": "neutral",
                "score": 0.0,
                "themes": [],
                "intent": "other",
                "action_items": [],
                "confidence": 0.0,
                "error": str(e)
            },
            "model": model,
            "processing_latency_ms": int((time.time() - start) * 1000)
        }

    latency = int((time.time() - start) * 1000)

    # Try to parse JSON for extracted text
    import re
    parsed_txt = None
    try:
        parsed_txt = json.loads(raw)
    except Exception:
        m = re.search(r'(\{.*\})', raw, flags=re.DOTALL)
        if m:
            try:
                parsed_txt = json.loads(m.group(1))
            except Exception:
                parsed_txt = None

    extracted = parsed_txt.get("extracted_text") if parsed_txt else raw.strip()

    # Run text analysis on the extracted text
    analysis_result = analyze_text_real(extracted, model=DEFAULT_TEXT_MODEL)

    # Combine results: use extracted_text and analysis from text model
    result = {
        "extracted_text": extracted,
        "analysis": analysis_result.get("analysis"),
        "model": f"{model}+{DEFAULT_TEXT_MODEL}",
        "processing_latency_ms": latency
    }
    return result

# Public API for the app to import
def analyze_text(text: str, test_mode: bool = True) -> Dict[str, Any]:
    if test_mode:
        # keep using the existing mock behavior from services/gemini_client if you want,
        # but provide a small fallback here for local dev
        from services.gemini_client import analyze_text as mock_text
        return mock_text(text, test_mode=True)
    return analyze_text_real(text)

def analyze_image(image_bytes: bytes, test_mode: bool = True) -> Dict[str, Any]:
    if test_mode:
        from services.gemini_client import analyze_image as mock_image
        return mock_image(image_bytes, test_mode=True)
    return analyze_image_real(image_bytes)
