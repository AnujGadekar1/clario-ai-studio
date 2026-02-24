# Path: intelligent_summarizer/backend/routers/similarity.py

from fastapi import APIRouter
from pydantic import BaseModel
from services.embedding_engine import calculate_similarity

router = APIRouter()

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

@router.post("/similarity")
def similarity(request: SimilarityRequest):
    score = calculate_similarity(request.text1, request.text2)

    return {
        "similarity_score": score,
        "interpretation": interpret_score(score)
    }

def interpret_score(score):
    if score > 0.8:
        return "Highly Similar"
    elif score > 0.5:
        return "Moderately Similar"
    else:
        return "Low Similarity"
