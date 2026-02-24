from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI Text Analyzer API",
    description="A simple AI-powered text analysis service",
    version="1.0.0"
)

# Include API routes
app.include_router(router)