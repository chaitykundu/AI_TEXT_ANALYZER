# app/services/analyzer.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from app.core.config import settings
import requests
import pdfplumber
from docx import Document
from io import BytesIO
import re

# -------------------------------------------------
# Load embedding model once (important for performance)
# -------------------------------------------------
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully")


# -------------------------------------------------
# Utility: Clean Text
# -------------------------------------------------
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# -------------------------------------------------
# Utility: Extract Text From File
# -------------------------------------------------
async def extract_text_from_file(file):
    filename = file.filename.lower()
    file_bytes = await file.read()
    content = ""

    # File size validation (5MB)
    if len(file_bytes) > 5_000_000:
        raise ValueError("File too large. Maximum 5MB allowed.")

    if filename.endswith(".pdf"):
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    content += text + " "

    elif filename.endswith(".txt"):
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = file_bytes.decode("latin1")

    elif filename.endswith(".docx"):
        doc = Document(BytesIO(file_bytes))
        content = "\n".join([para.text for para in doc.paragraphs])

    else:
        raise ValueError("Unsupported file format. Only PDF, DOCX, and TXT allowed.")

    return clean_text(content)


# -------------------------------------------------
# Semantic Similarity
# -------------------------------------------------
def compute_semantic_similarity(text1: str, text2: str) -> float:
    embeddings = embedding_model.encode([text1, text2])
    similarity = cosine_similarity(
        [embeddings[0]], [embeddings[1]]
    )[0][0]
    return round(float(similarity) * 100, 2)


# -------------------------------------------------
# Extract Skills from JD (dynamic)
# -------------------------------------------------
def extract_skills_from_jd(job_description: str):
    words = re.findall(r'\b[A-Za-z\+\#]+\b', job_description)
    return list(set(words))


# -------------------------------------------------
# Semantic Skill Matching
# -------------------------------------------------
def semantic_skill_match(resume_text, skills, threshold=0.6):
    resume_embedding = embedding_model.encode([resume_text])[0]
    found = []

    for skill in skills:
        skill_embedding = embedding_model.encode([skill])[0]
        similarity = cosine_similarity(
            [resume_embedding],
            [skill_embedding]
        )[0][0]

        if similarity > threshold:
            found.append(skill)

    return found


# -------------------------------------------------
# Extract Experience Years
# -------------------------------------------------
def extract_experience_years(text):
    matches = re.findall(r'(\d+)\+?\s+years', text.lower())
    if matches:
        return max([int(x) for x in matches])
    return 0


# -------------------------------------------------
# Detect Resume Sections
# -------------------------------------------------
def detect_sections(text):
    sections = {
        "experience": "experience" in text.lower(),
        "education": "education" in text.lower(),
        "projects": "project" in text.lower(),
        "skills_section": "skills" in text.lower()
    }
    return sections


# -------------------------------------------------
# Existing Text Analyzer (Kept)
# -------------------------------------------------
def analyze_text(text: str, use_gemini: bool = False):
    if use_gemini and settings.GEMINI_API_KEY:
        gemini_result = analyze_text_with_gemini(text)
        if gemini_result:
            return gemini_result

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


# -------------------------------------------------
# Gemini API Call (Kept)
# -------------------------------------------------
def analyze_text_with_gemini(text: str):
    url = "https://api.gemini.example/analyze"
    headers = {"Authorization": f"Bearer {settings.GEMINI_API_KEY}"}
    payload = {"text": text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Gemini API error:", e)
        return None


# -------------------------------------------------
# 🔥 ADVANCED RESUME ANALYZER
# -------------------------------------------------
async def analyze_resume(file, job_description: str = None):

    # 1️⃣ Extract Resume Text
    content = await extract_text_from_file(file)

    if not content:
        raise ValueError("No readable content found in resume.")

    # 2️⃣ Dynamic Skill List
    if job_description:
        skill_list = extract_skills_from_jd(job_description)
    else:
        skill_list = ["Python", "Machine Learning", "SQL", "Data", "NLP", "AI"]

    # 3️⃣ Semantic Skill Matching
    skills_found = semantic_skill_match(content, skill_list)
    skill_score = (
        (len(skills_found) / len(skill_list)) * 100
        if skill_list else 0
    )

    # 4️⃣ Resume ↔ JD Similarity
    semantic_score = 0
    if job_description:
        semantic_score = compute_semantic_similarity(content, job_description)

    # 5️⃣ Experience Score
    years = extract_experience_years(content)
    experience_score = min(years * 10, 100)

    # 6️⃣ Section Completeness Score
    sections = detect_sections(content)
    section_score = (
        sum(sections.values()) / len(sections) * 100
    )

    # 7️⃣ Word Count
    word_count = len(content.split())

    # 8️⃣ Final ATS Weighted Score
    final_score = (
        0.35 * skill_score +
        0.35 * semantic_score +
        0.15 * experience_score +
        0.15 * section_score
    )

    return {
        "skills_found": skills_found,
        "skill_score": round(skill_score, 2),
        "semantic_match_score": round(semantic_score, 2),
        "experience_years_detected": years,
        "experience_score": round(experience_score, 2),
        "section_score": round(section_score, 2),
        "final_score": round(final_score, 2),
        "word_count": word_count
    }