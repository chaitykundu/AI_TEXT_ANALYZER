from fastapi import APIRouter
from app.models.schema import TextRequest, TextResponse
from app.services.analyzer import analyze_text

router = APIRouter()

@router.get("/")
def root():
    return {"message": "AI Text Analyzer API is running"}

@router.post("/analyze", response_model=TextResponse)
def analyze(request: TextRequest):
    result = analyze_text(request.text)
    return result