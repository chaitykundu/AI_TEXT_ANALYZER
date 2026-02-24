from fastapi import APIRouter, File, UploadFile
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
async def analyze_resume_endpoint(file: UploadFile = File(...), use_gemini: bool = True):
    """
    Upload a PDF/TXT resume.
    use_gemini=True to utilize Gemini API for analysis.
    Returns: skill score, text summary, sentiment, and polarity
    """
    result = await analyze_resume(file, use_gemini=use_gemini)
    return result