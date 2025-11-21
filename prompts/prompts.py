# prompts/prompts.py
# Small library of prompt templates for Consumer Sense AI.

def build_vision_prompt():
    """
    Prompt for Gemini Vision to extract text from a screenshot.
    Keeps the output extremely controlled.
    """
    return (
        "You are an OCR assistant.\n"
        "Extract ONLY the customer review text from the screenshot.\n"
        "Return strictly this JSON:\n"
        "{\n"
        "  \"extracted_text\": \"...\"\n"
        "}\n"
        "Rules:\n"
        "- Preserve emojis and punctuation.\n"
        "- If multiple comments exist, choose the main review block.\n"
        "- Only output valid JSON. No explanations."
    )

def analysis_prompt():
    """
    Prompt to send to Gemini Text for analysis. This prompt asks for strict JSON output.
    Replace {{TEXT}} with the review text before sending.
    """
    return (
        "You are a text-analysis assistant. Given the customer review contained between triple backticks, "
        "produce a single valid JSON object with the following fields:\n"
        "  - text: cleaned review text (string)\n"
        "  - sentiment: one of [\"positive\", \"neutral\", \"negative\", \"mixed\"]\n"
        "  - score: sentiment score between -1.0 (very negative) and 1.0 (very positive)\n"
        "  - themes: array of short theme strings (e.g., [\"checkout\", \"delivery\"]) - top 3\n"
        "  - intent: one of [\"complaint\",\"praise\",\"feature_request\",\"question\",\"other\"]\n"
        "  - action_items: array of 0-3 suggested action items (strings) for product/support teams\n"
        "  - confidence: a number between 0.0 and 1.0 representing model confidence\n"
        "Return ONLY valid JSON (no surrounding text). Use temperature 0 for deterministic output.\n\n"
        "Example input:\n"
        "```{{TEXT}}```\n\n"
        "Example output schema (must follow):\n"
        "{\"text\":\"...\",\"sentiment\":\"negative\",\"score\":-0.6,"
        "\"themes\":[\"checkout\",\"crash\"],\"intent\":\"complaint\","
        "\"action_items\":[\"Investigate logs\",\"Add retry\"],\"confidence\":0.92}\n"
    )
