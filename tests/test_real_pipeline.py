print("DEBUG: 🟢 Python is reading the test file...")
import unittest
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.gemini_rest import GeminiREST

class TestRealPipeline(unittest.TestCase):
    def setUp(self):
        print("DEBUG: Setting up test...")
        load_dotenv()
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("DEBUG: No API Key found!")
            self.skipTest("⚠️ GEMINI_API_KEY not found. Skipping real integration test.")
        
        self.client = GeminiREST(self.api_key)

    def test_complex_review_parsing(self):
        """
        Tests if the model can parse a complex, unstructured Amazon-style review
        and extract Product Manager insights (Pain Points, Metadata).
        """
        print("\n🧪 Testing Product Manager Parsing (Gemini 2.5)...")
        
        raw_text = """
        sivakumar
        4.0 out of 5 stars
        Decent keyboard.. But basic functionality missing.
        Reviewed in India on 31 January 2025
        Colour: WhiteVerified Purchase
        The real problem is the caps lock key. If pressed, the keyboard do not have any indication if it is on or off.
        """
        
        result = self.client.analyze_review(text=raw_text)
        analysis = result["analysis"]
        
        print(f"   Analyzed: {len(analysis.get('rich_reviews', []))} review(s) detected.")

        # Validation
        self.assertIn("rich_reviews", analysis)
        self.assertIn("overall_summary", analysis)
        
        first_review = analysis["rich_reviews"][0]
        metadata = first_review.get("metadata", {})
        insights = first_review.get("analysis", {})

        self.assertIn("sivakumar", metadata.get("username", "").lower())
        
        pain_points = str(insights.get("pain_points", [])).lower()
        self.assertIn("caps lock", pain_points)
        
        print("✅ Successfully extracted Metadata & Pain Points!")

if __name__ == "__main__":
    unittest.main()