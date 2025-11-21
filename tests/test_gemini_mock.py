# tests/test_gemini_mock.py
import sys
sys.path.insert(0, ".")

from services.gemini_client import analyze_text, analyze_image

def main():
    # Test text analysis
    text = "The checkout crashed and I lost my cart 😕"
    result = analyze_text(text, test_mode=True)
    print("TEXT ANALYSIS RESULT:")
    print(result)

    # Test image analysis (will use mock OCR)
    fake_bytes = b"checkout cart crash"
    img_result = analyze_image(fake_bytes, test_mode=True)
    print("\nIMAGE ANALYSIS RESULT:")
    print(img_result)

if __name__ == "__main__":
    main()
