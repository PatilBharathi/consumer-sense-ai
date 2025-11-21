# tests/run_prompt_schema_test.py
import sys
import json
from datetime import datetime, timezone

# allow imports from repo root
sys.path.insert(0, ".")

from workers.schema_validator import validate_review_doc
from prompts.prompts import analysis_prompt

def make_mock_analysis():
    """
    Mock the structured JSON that Gemini Text *should* return.
    This matches the analysis_prompt's schema (no 'text' field in analysis).
    """
    return {
        "sentiment": "negative",
        "score": -0.65,
        "themes": ["checkout", "crash"],
        "intent": "complaint",
        "action_items": ["Investigate logs for checkout failure", "Add retry/save-cart"],
        "confidence": 0.92
    }

def build_full_doc(analysis: dict):
    now = datetime.now(timezone.utc).isoformat()
    return {
      "review_id": "mock-uuid-001",
      "source": "mobile_app_screenshot",
      "user_id_hash": None,
      "raw_text": "Mock: the checkout crashed and I lost my cart.",
      "extracted_text": "Mock: the checkout crashed and I lost my cart.",
      "analysis": analysis,
      "image_gcs_path": None,
      "language": "en",
      "model": "gemini-1.5-mini",
      "processing_latency_ms": 850,
      "created_at": now,
      "processed_at": now,
      "metadata": {"app_version":"1.0.0", "region":"IN", "upload_method":"web_ui"}
    }

def main():
    # Show the prompt (for clarity) - not required
    print("Using analysis prompt template (example):")
    print(analysis_prompt().splitlines()[0])  # first line for brevity

    mock_text = "Mock: the checkout crashed and I lost my cart."
    analysis = make_mock_analysis()
    doc = build_full_doc(analysis)

    ok, errors = validate_review_doc(doc)
    if ok:
        print("OK: mock document is valid against schema.")
    else:
        print("INVALID: mock document failed validation.")
        for e in errors:
            print(" -", e)
        sys.exit(2)

if __name__ == "__main__":
    main()
