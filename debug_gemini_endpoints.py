import os
import sys

# Ensure we can import from services/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini_rest import GeminiREST

def main():
    print("🔍 Testing GeminiREST Service (SDK Integration)...")

    # 1. Check Env Var
    if "GEMINI_API_KEY" not in os.environ:
        print("❌ GEMINI_API_KEY not found in environment variables.")
        print("   Please run: set GEMINI_API_KEY=your_key_here (Windows) or export GEMINI_API_KEY=... (Mac/Linux)")
        return

    try:
        # 2. Initialize Service
        # The new class automatically picks up GEMINI_API_KEY from os.environ
        client = GeminiREST()
        print("✅ Service Initialized")

        # 3. Test Text Analysis
        print("\n🧠 Testing Text Analysis...")
        text_result = client.text_analyze("This product is terrible. I want a refund immediately.")
        print(f"   Result: {text_result}")
        
        if text_result.get("sentiment") == "negative":
            print("✅ Text Analysis Logic: PASS")
        else:
            print("⚠️ Text Analysis Logic: Check results (expected negative)")

        # 4. Test Combined Flow (Text only)
        print("\n🔄 Testing Combined analyze_review (Text only)...")
        combined = client.analyze_review(text="I love this service! Best hackathon ever.")
        print(f"   Result: {combined['analysis']}")
        
        if combined['analysis'].get("sentiment") == "positive":
            print("✅ Combined Flow: PASS")
        else:
            print("⚠️ Combined Flow: Check results")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()