# Path: intelligent_summarizer/backend/routers/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from services.file_parser import extract_text_from_pdf, extract_text_from_docx
from services.analysis import analyze_text
from services.advanced_summarizer import advanced_summary
from services.neural_refiner import neural_coherence_refinement

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (Max 10MB)")

    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX supported")

    file.file.seek(0)

    try:
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file.file)
        else:
            text = extract_text_from_docx(file.file)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found")

        summary = advanced_summary(text, "standard")

        # Trim for safety
        words = summary.split()
        if len(words) > 300:
            summary = " ".join(words[:300])

        summary = await neural_coherence_refinement(summary)

        analysis = analyze_text(text)

        return {
            "filename": file.filename,
            "summary": summary,
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
