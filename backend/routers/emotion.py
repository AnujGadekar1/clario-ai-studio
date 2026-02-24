# Path: intelligent_summarizer/backend/routers/emotion.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from services.file_parser import extract_text_from_pdf, extract_text_from_docx
from services.emotion_service import analyze_text_emotion

router = APIRouter()


class EmotionTextRequest(BaseModel):
    text: str


@router.post("/emotion/text")
def analyze_emotion_text(payload: EmotionTextRequest):
    """
    Analyze emotion directly from raw text.
    Returns:
    {
        emotion: {...},
        subjectivity: {...}
    }
    """

    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = analyze_text_emotion(payload.text)

    return result


@router.post("/emotion/file")
async def analyze_emotion_file(file: UploadFile = File(...)):
    """
    Analyze emotion from uploaded PDF or DOCX.
    Returns SAME structure as /emotion/text for consistency.
    """

    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX supported")

    file.file.seek(0)

    try:
        # Extract text
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file.file)
        else:
            text = extract_text_from_docx(file.file)

        if not text or len(text.strip()) < 20:
            raise HTTPException(status_code=400, detail="No readable text extracted from file")

        # Run emotion analysis
        result = analyze_text_emotion(text)

        # IMPORTANT: return same structure as text route
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotion analysis failed: {str(e)}")