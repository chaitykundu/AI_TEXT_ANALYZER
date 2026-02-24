from pydantic import BaseModel

class TextRequest(BaseModel):
    text: str

class TextResponse(BaseModel):
    word_count: int
    sentiment: str
    polarity_score: float