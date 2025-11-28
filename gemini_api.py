# file: gemini_api.py
import os
import google.generativeai as genai

# Load Gemini API Key from environment or fallback (for demo)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBmuSV71p37CStl5TPe5XjqNTYNgtiS9ZI")

# Configure Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(prompt: str) -> str:
    """
    Calls the Gemini API with a text prompt and returns the response.
    Keeps it simple for clarity and debugging.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini Error] {e}"
