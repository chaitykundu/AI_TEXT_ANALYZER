import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

class Settings:
    APP_NAME = "AI Text Analyzer"
    DEBUG = True
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Read from .env

settings = Settings()