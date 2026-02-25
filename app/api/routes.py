from fastapi import APIRouter, File, UploadFile, Form
from app.models.schema import TextRequest, TextResponse
from app.services.analyzer import analyze_text, analyze_resume

router = APIRouter()

# Root endpoint
@router.get("/")
def root():
    return {"message": "AI Text Analyzer API is running"}

# Original Text Analyzer endpoint (kept separate)
@router.post("/analyze", response_model=TextResponse)
def analyze(request: TextRequest, use_gemini: bool = False):
    result = analyze_text(request.text, use_gemini=use_gemini)
    return result

# Resume Analyzer endpoint (new)
@router.post("/analyze_resume")
async def analyze_resume_endpoint(
    file: UploadFile = File(...),
    job_description: str = Form(None)
):
    """
    Upload a resume (PDF/TXT).
    Optionally provide a job description for semantic matching.
    
    Returns:
    - skill_score
    - semantic_match_score (if JD provided)
    - final_score
    - skills_found
    - word_count
    """
    result = await analyze_resume(file, job_description)
    return result