from textblob import TextBlob
from app.core.config import settings
import requests

def analyze_text_with_gemini(text: str):
    url = "https://api.gemini.example/analyze"  # Replace with real Gemini API URL
    headers = {
        "Authorization": f"Bearer {settings.GEMINI_API_KEY}"
    }
    payload = {"text": text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()  # Expect Gemini to return structured result
    except Exception as e:
        print("Gemini API error:", e)
        return None

def analyze_text(text: str, use_gemini: bool = False):
    if use_gemini and settings.GEMINI_API_KEY:
        gemini_result = analyze_text_with_gemini(text)
        if gemini_result:
            return gemini_result  # Return Gemini API result directly
        # If Gemini fails, fallback to TextBlob

    # Fallback to TextBlob analysis
    words = text.split()
    word_count = len(words)

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "word_count": word_count,
        "sentiment": sentiment,
        "polarity_score": round(polarity, 3)
    }