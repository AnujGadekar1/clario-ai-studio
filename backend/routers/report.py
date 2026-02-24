# Path: intelligent_summarizer/backend/routers/report.py

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from services.report_generator import generate_pdf_report

router = APIRouter()


class ReportRequest(BaseModel):
    summary: str
    analysis: dict


@router.post("/generate-report")
def generate_report(payload: ReportRequest):

    file_path = generate_pdf_report(payload.dict())

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="AI_Report.pdf"
    )
