import os
import time
from typing import Dict, Optional, List, Union
from dotenv import load_dotenv # Import dotenv
from services.gemini_rest import GeminiREST

# FORCE LOAD .env here to ensure this module sees the keys
load_dotenv()

USE_REAL = os.environ.get("USE_REAL_GEMINI", "false").lower() == "true"
API_KEY = os.environ.get("GEMINI_API_KEY", None)

# DEBUG PRINT: This will show up in your terminal when you start the app
print(f"🔌 GeminiClient Init: USE_REAL={USE_REAL}, Key Found={'Yes' if API_KEY else 'No'}")

_gemini_client: Optional[GeminiREST] = None

def _get_gemini():
    global _gemini_client
    if _gemini_client is None:
        if not USE_REAL:
            return None
        print("🔹 Initializing Real Gemini Client...")
        _gemini_client = GeminiREST(API_KEY)
    return _gemini_client

# -------------------------
# analyze_image
# -------------------------
def analyze_image(images: Union[bytes, List[bytes]], test_mode: bool = False) -> Dict:
    if USE_REAL and not test_mode:
        client = _get_gemini()
        print("📸 Sending Image to Gemini...")
        start = time.time()
        
        image_list = images if isinstance(images, list) else [images]
        resp = client.analyze_review(images=image_list)
        
        return {
            "input_text": resp.get("input_text"),
            "extracted_text": resp.get("extracted_text"),
            "analysis": resp.get("analysis"),
            "model": "gemini-2.5-flash (real)",
            "processing_latency_ms": int((time.time() - start) * 1000)
        }

    return {"input_text": "Mock", "extracted_text": "Mock", "analysis": {}, "model": "mock", "processing_latency_ms": 5}

# -------------------------
# analyze_text
# -------------------------
def analyze_text(text: str, test_mode: bool = False) -> Dict:
    # Debug print to check logic
    if USE_REAL:
        print("✅ Text Analysis: Real Mode Active")
    else:
        print("❌ Text Analysis: Real Mode INACTIVE (Using Mock)")

    if USE_REAL and not test_mode:
        client = _get_gemini()
        print("📝 Sending Text/URL Content to Gemini...")
        start = time.time()
        
        resp = client.analyze_review(text=text)
        
        print(f"   ✅ Received keys: {list(resp.get('analysis', {}).keys())}")
        
        return {
            "input_text": resp.get("input_text"),
            "extracted_text": resp.get("extracted_text"),
            "analysis": resp.get("analysis"),
            "model": "gemini-2.5-pro (real)",
            "processing_latency_ms": int((time.time() - start) * 1000)
        }
    
    print("⚠️ Warning: Returning Mock Data")
    return {
        "input_text": text,
        "extracted_text": text,
        "analysis": {
            "sentiment": "Neutral", 
            "themes": [], 
            "intent": "unknown",
            "score": 0.5,
            "confidence": 0.8,
            "overall_summary": "Mock Summary",
            "top_level_advice": "Mock Advice"
        },
        "model": "mock",
        "processing_latency_ms": 3
    }