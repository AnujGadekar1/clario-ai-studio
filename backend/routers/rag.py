# Path: intelligent_summarizer/backend/routers/rag.py

from fastapi import APIRouter
from pydantic import BaseModel
from services.rag_engine import rag_engine

router = APIRouter()


class RAGBuildRequest(BaseModel):
    text: str


class RAGQueryRequest(BaseModel):
    question: str


@router.post("/rag/build")
def build_rag(request: RAGBuildRequest):
    rag_engine.build_index(request.text)
    return {"message": "RAG index built successfully"}


@router.post("/rag/query")
async def query_rag(request: RAGQueryRequest):
    answer = await rag_engine.query(request.question)
    return {"answer": answer}
