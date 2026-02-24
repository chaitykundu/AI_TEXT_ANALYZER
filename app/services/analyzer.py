# app/services/analyzer.py

from textblob import TextBlob
from app.core.config import settings
import requests
import pdfplumber
from io import BytesIO

# ------------------------------
# Text Analyzer (existing)
# ------------------------------
def analyze_text(text: str, use_gemini: bool = False):
    """
    Analyze plain text for word count, sentiment, and optional Gemini API analysis.
    """
    # Use Gemini API if enabled
    if use_gemini and settings.GEMINI_API_KEY:
        gemini_result = analyze_text_with_gemini(text)
        if gemini_result:
            return gemini_result  # Return Gemini API result directly

    # Fallback: TextBlob analysis
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

# ------------------------------
# Gemini API call
# ------------------------------
def analyze_text_with_gemini(text: str):
    """
    Call Gemini API to analyze text. Returns JSON or None on failure.
    """
    url = "https://api.gemini.example/analyze"  # Replace with real Gemini API URL
    headers = {"Authorization": f"Bearer {settings.GEMINI_API_KEY}"}
    payload = {"text": text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Gemini API error:", e)
        return None

# ------------------------------
# Resume Analyzer
# ------------------------------
async def analyze_resume(file, use_gemini: bool = True):
    """
    Analyze uploaded resume file (PDF/TXT).
    Returns: skill_score, skills_found, text summary, sentiment, polarity
    """
    # Extract text from file
    content = ""
    filename = file.filename.lower()
    file_bytes = await file.read()

    if filename.endswith(".pdf"):
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                content += page.extract_text() + " "
    else:
        # TXT fallback
        content = file_bytes.decode()

    # Analyze text (TextBlob or Gemini)
    analysis = analyze_text(content, use_gemini=use_gemini)

    # Simple skill scoring example
    skill_keywords = ["Python", "Machine Learning", "SQL", "Data", "NLP", "AI"]
    skills_found = [k for k in skill_keywords if k.lower() in content.lower()]
    skill_score = len(skills_found) / len(skill_keywords) * 100

    # Return combined result
    return {
        "text_summary": content[:500] + ("..." if len(content) > 500 else ""),
        "skill_score": round(skill_score, 2),
        "skills_found": skills_found,
        **analysis
    }