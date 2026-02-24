# Path: intelligent_summarizer/backend/services/advanced_summarizer.py

import torch
from transformers import pipeline
from services.summarizer import generate_summary

# ---------------------------------------------------
# DEVICE CONFIGURATION
# ---------------------------------------------------

device = 0 if torch.cuda.is_available() else -1  # Auto GPU if available

# ---------------------------------------------------
# LOAD SUMMARIZATION MODEL (Once)
# ---------------------------------------------------

summarizer_model = pipeline(
    "summarization",
    model="facebook/bart-base",
    device=device
)

# ---------------------------------------------------
# ADVANCED SUMMARY FUNCTION
# ---------------------------------------------------

def advanced_summary(text: str, mode: str = "standard", custom_words: int | None = None) -> str:

    if not text.strip():
        return "No content provided."

    # Safety trim for extremely long inputs
    text = text[:20000]

    # ---------------------------------------------------
    # LENGTH CONFIGURATION
    # ---------------------------------------------------

    if mode == "short":
        ratio = 0.3
        max_len = 100
        min_len = 40

    elif mode == "detailed":
        ratio = 0.7
        max_len = 300
        min_len = 120

    elif mode == "custom" and custom_words:
        ratio = 0.6  # Balanced reduction before model stage

        # Model max token limit protection
        max_len = min(512, custom_words + 20)
        min_len = max(20, int(custom_words * 0.7))

    else:  # standard
        ratio = 0.5
        max_len = 180
        min_len = 60

    # ---------------------------------------------------
    # STAGE 1: Extractive Reduction
    # ---------------------------------------------------

    reduced_text = generate_summary(text, ratio)

    # Additional safety trimming
    reduced_text = reduced_text[:4000]

    # ---------------------------------------------------
    # STAGE 2: Abstractive Summarization (BART)
    # ---------------------------------------------------

    try:
        result = summarizer_model(
            reduced_text,
            max_length=max_len,
            min_length=min_len,
            do_sample=False,
            truncation=True
        )

        final_summary = result[0]["summary_text"].strip()

        return final_summary

    except Exception:
        # Safe fallback to extractive summary
        return reduced_text