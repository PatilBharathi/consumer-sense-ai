# tests/print_prompts.py
import sys
sys.path.insert(0, ".")

from prompts.prompts import build_vision_prompt, analysis_prompt

SAMPLE_TEXT = "I love the new update but the checkout crashed and I lost my cart 😕"

def main():
    print("=== VISION PROMPT ===")
    print(build_vision_prompt())
    print("\n=== ANALYSIS PROMPT (with text inserted) ===")
    prompt = analysis_prompt().replace("{{TEXT}}", SAMPLE_TEXT)
    print(prompt)

if __name__ == "__main__":
    main()
