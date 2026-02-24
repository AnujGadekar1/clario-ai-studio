# Path: intelligent_summarizer/backend/routers/enhancer.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch

router = APIRouter()

# Use instruction-tuned model (much better than t5-small)
MODEL_NAME = "google/flan-t5-base"

device = 0 if torch.cuda.is_available() else -1

enhancer_model = pipeline(
    "text2text-generation",
    model=MODEL_NAME,
    device=device
)


class EnhanceRequest(BaseModel):
    text: str
    mode: str


def build_prompt(text: str, mode: str) -> str:
    base_instruction = (
        "You are an expert writing assistant. "
        "Rewrite the text while preserving the original meaning. "
        "Improve clarity, grammar, structure, and readability.\n\n"
    )

    mode_instructions = {
        "improve": "Make the writing clearer and more polished.",
        "academic": "Rewrite in a formal academic tone with precise language.",
        "professional": "Rewrite in a professional business tone.",
        "simplify": "Simplify the language so it is easy to understand.",
        "paraphrase": "Paraphrase the text using different wording while keeping the meaning."
    }

    instruction = mode_instructions.get(mode, mode_instructions["improve"])

    return f"{base_instruction}{instruction}\n\nText:\n{text}"


@router.post("/enhance-text")
def enhance_text(payload: EnhanceRequest):

    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text required")

    text = payload.text.strip()

    prompt = build_prompt(text, payload.mode)

    # Dynamic length control
    input_length = len(text.split())
    max_length = min(512, int(input_length * 1.8) + 40)
    min_length = max(20, int(input_length * 0.6))

    result = enhancer_model(
        prompt,
        max_length=max_length,
        min_length=min_length,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.2,
        do_sample=True
    )

    enhanced = result[0]["generated_text"].strip()

    return {
        "enhanced_text": enhanced
    }
