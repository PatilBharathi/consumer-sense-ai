import os
import json
from google import genai
from google.genai import types
from PIL import Image
import io

class GeminiREST:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found in env. Ensure it is set.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_flash = "gemini-2.5-flash"

    def analyze_content(self, images: list = None, text_input: str = None):
        prompt = (
            "You are a Senior Product Manager. Your goal is to extract strategic insights from user feedback.\n\n"
            "INPUT CONTEXT:\n"
            "The input is text or images (screenshots).\n\n"
            "CRITICAL INSTRUCTION:\n"
            "Look carefully at the visual structure. If you see multiple reviews in one image (separated by lines, spacing, or different usernames), EXTRACT EACH ONE SEPARATELY.\n\n"
            "DECISION LOGIC:\n"
            "1. IF user reviews are detected: Create a separate entry for EACH distinct review found.\n"
            "2. IF only product text is found: Analyze the product claims (SWOT analysis).\n\n"
            "OUTPUT FORMAT (JSON Only):\n"
            "{\n"
            "  \"reviews\": [\n"
            "    {\n"
            "      \"metadata\": {\"username\": \"...\", \"rating\": \"...\", \"date\": \"...\"},\n"
            "      \"text\": \"...\",\n"
            "      \"analysis\": {\n"
            "         \"sentiment\": \"Positive/Negative/Neutral\",\n"
            "         \"pain_points\": [\"...\"],\n"
            "         \"feature_requests\": [\"...\"],\n"
            "         \"actionable_advice\": \"...\"\n"
            "      }\n"
            "    }\n"
            "  ],\n"
            "  \"overall_summary\": \"Strategic Executive Summary of ALL feedback provided.\",\n"
            "  \"analysis\": {\n"
            "      \"sentiment\": \"Overall Sentiment\",\n"
            "      \"pain_points\": [\"Top 3 global pain points\"],\n"
            "      \"feature_requests\": [\"Top 3 global requests\"],\n"
            "      \"actionable_advice\": \"High-level strategic recommendation.\"\n"
            "  }\n"
            "}"
        )

        contents = [prompt]

        if images:
            for img_bytes in images:
                try:
                    image = Image.open(io.BytesIO(img_bytes))
                    contents.append(image)
                except Exception as e:
                    print(f"Skipping invalid image: {e}")
        
        if text_input:
            contents.append(f"User Input Text:\n{text_input}")

        try:
            response = self.client.models.generate_content(
                model=self.model_flash,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)

        except Exception as e:
            print(f"❌ Analysis Error: {e}")
            return {
                "reviews": [],
                "overall_summary": f"Error processing request: {str(e)}"
            }

    def analyze_review(self, images=None, text=None):
        image_list = images if isinstance(images, list) else ([images] if images else [])
        
        result = self.analyze_content(images=image_list, text_input=text)
        
        raw_reviews = result.get("reviews", [])
        valid_reviews = []

        # RELAXED FILTER: Show review if it has ANY meaningful text
        for r in raw_reviews:
            has_text = len(r.get("text", "") or "") > 5
            if has_text:
                valid_reviews.append(r)

        analysis_block = result.get("analysis", {})

        enhanced_analysis = {
            "sentiment": analysis_block.get("sentiment", "Neutral"),
            "themes": analysis_block.get("pain_points", []) + analysis_block.get("feature_requests", []),
            "intent": "See actionable_advice",
            "score": 0.9 if analysis_block.get("sentiment") == "Positive" else 0.5,
            "confidence": 0.99,
            "rich_reviews": valid_reviews,
            "overall_summary": result.get("overall_summary") or "No summary generated.",
            "top_level_advice": analysis_block.get("actionable_advice") or "No specific advice generated.",
            "top_level_pains": analysis_block.get("pain_points", []),
            "top_level_features": analysis_block.get("feature_requests", [])
        }

        return {
            "input_text": text or f"{len(image_list)} Images Processed",
            "extracted_text": "Content processed by Gemini", 
            "analysis": enhanced_analysis,
        }