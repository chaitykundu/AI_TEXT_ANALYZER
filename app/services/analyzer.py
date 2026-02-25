# app/services/analyzer.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from textblob import TextBlob
from app.core.config import settings
import requests
import pdfplumber
from io import BytesIO


# Load embedding model once
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_semantic_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts.
    Returns percentage score (0-100).
    """
    embeddings = embedding_model.encode([text1, text2])
    similarity = cosine_similarity(
        [embeddings[0]], [embeddings[1]]
    )[0][0]

    return round(float(similarity) * 100, 2)

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
async def analyze_resume(file, job_description: str = None):
    content = ""
    filename = file.filename.lower()
    file_bytes = await file.read()

    if filename.endswith(".pdf"):
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                content += page.extract_text() + " "
    else:
        content = file_bytes.decode()

    # Basic keyword skill scoring
    skill_keywords = ["Python", "Machine Learning", "SQL", "Data", "NLP", "AI"]
    skills_found = [k for k in skill_keywords if k.lower() in content.lower()]
    skill_score = len(skills_found) / len(skill_keywords) * 100

    # Word count
    word_count = len(content.split())

    # Semantic matching (if JD provided)
    semantic_score = None
    if job_description:
        semantic_score = compute_semantic_similarity(content, job_description)

    # Weighted final score
    final_score = skill_score
    if semantic_score:
        final_score = (0.6 * skill_score) + (0.4 * semantic_score)

    return {
        "skills_found": skills_found,
        "skill_score": round(skill_score, 2),
        "semantic_match_score": semantic_score,
        "final_score": round(final_score, 2),
        "word_count": word_count
    }