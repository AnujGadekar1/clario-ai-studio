# Path: intelligent_summarizer/backend/routers/summarize.py

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from services.advanced_summarizer import advanced_summary
from services.analysis import analyze_text
from services.neural_refiner import neural_coherence_refinement
from core.limiter import limiter

router = APIRouter()


# ---------------------------------------------------
# REQUEST MODEL
# ---------------------------------------------------

class TextRequest(BaseModel):
    text: str
    mode: str = "standard"
    custom_word_count: Optional[int] = None


# ---------------------------------------------------
# SUMMARIZE ROUTE
# ---------------------------------------------------

@router.post("/summarize")
@limiter.limit("10/minute")
async def summarize_text(request: Request, payload: TextRequest):

    # -------------------------
    # Input Validation
    # -------------------------
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    text = payload.text.strip()

    # Optional safety limit for very long input
    text = text[:20000]

    # -------------------------
    # Stage 1: Summary Generation
    # -------------------------
    if payload.mode == "custom":

        if not payload.custom_word_count:
            raise HTTPException(
                status_code=400,
                detail="Custom word count required for custom mode"
            )

        if payload.custom_word_count < 20 or payload.custom_word_count > 500:
            raise HTTPException(
                status_code=400,
                detail="Custom word count must be between 20 and 500"
            )

        summary = advanced_summary(
            text,
            mode="custom",
            custom_words=payload.custom_word_count
        )

    else:
        summary = advanced_summary(text, payload.mode)

    # -------------------------
    # Stage 2: Gemini Refinement
    # -------------------------
    summary = await neural_coherence_refinement(summary)

    # -------------------------
    # Stage 3: Full Analysis
    # -------------------------
    analysis = analyze_text(text)

    # -------------------------
    # Response
    # -------------------------
    return {
        "summary": summary,
        "analysis": analysis
    }