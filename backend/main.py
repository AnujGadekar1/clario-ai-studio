# Path: intelligent_summarizer/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from routers import summarize
from routers import similarity
from routers import rag
from routers import upload
from routers import report
from routers import enhancer 
from core.limiter import limiter
from routers import emotion

app = FastAPI(title="Intelligent Summarizer")

# Attach limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(summarize.router)
app.include_router(similarity.router)
app.include_router(rag.router)
app.include_router(upload.router)
app.include_router(report.router)
app.include_router(enhancer.router)
app.include_router(emotion.router)

@app.get("/")
def root():
    return {"message": "Intelligent Summarizer API Running"}

