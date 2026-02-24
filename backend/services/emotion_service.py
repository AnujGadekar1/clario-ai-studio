# Path: intelligent_summarizer/backend/services/emotion_service.py

from transformers import pipeline
from textblob import TextBlob
import torch
from typing import Dict, List

# ---------------------------------------------------
# DEVICE CONFIGURATION
# ---------------------------------------------------

device: int = 0 if torch.cuda.is_available() else -1

# ---------------------------------------------------
# LOAD MODEL ONCE (Global)
# ---------------------------------------------------

emotion_model = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    device=device,
    return_all_scores=True  # Needed for averaging
)

# ---------------------------------------------------
# TEXT CHUNKING (for long PDFs)
# ---------------------------------------------------

def split_text_into_chunks(text: str, max_words: int = 400) -> List[str]:
    words = text.split()
    chunks: List[str] = []

    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)

    return chunks


# ---------------------------------------------------
# EMOTION ANALYSIS
# ---------------------------------------------------

def analyze_emotion(text: str) -> Dict[str, float | str]:
    if not text.strip():
        return {"emotion": "neutral", "confidence": 0.0}

    # Safety limit to prevent overload
    text = text[:10000]

    chunks = split_text_into_chunks(text)

    emotion_scores: Dict[str, float] = {}

    try:
        for chunk in chunks:
            results = emotion_model(chunk)

            for item in results[0]:
                label: str = item["label"]
                score: float = float(item["score"])

                emotion_scores[label] = emotion_scores.get(label, 0.0) + score

        if not emotion_scores:
            return {"emotion": "neutral", "confidence": 0.0}

        # Average scores
        for label in emotion_scores:
            emotion_scores[label] /= len(chunks)

        # Safely get dominant emotion (Pylance-safe)
        dominant_emotion: str = max(
            emotion_scores.items(),
            key=lambda x: x[1]
        )[0]

        confidence: float = emotion_scores[dominant_emotion]

        return {
            "emotion": dominant_emotion,
            "confidence": round(confidence, 3)
        }

    except Exception:
        return {"emotion": "neutral", "confidence": 0.0}


# ---------------------------------------------------
# SUBJECTIVITY ANALYSIS
# ---------------------------------------------------

def analyze_subjectivity(text: str) -> Dict[str, float | str]:
    if not text.strip():
        return {"subjectivity_score": 0.0, "type": "objective"}

    blob = TextBlob(text)
    score: float = blob.sentiment.subjectivity

    return {
        "subjectivity_score": round(score, 3),
        "type": "subjective" if score > 0.5 else "objective"
    }


# ---------------------------------------------------
# MAIN PUBLIC FUNCTION
# ---------------------------------------------------

def analyze_text_emotion(text: str) -> Dict[str, Dict]:
    emotion = analyze_emotion(text)
    subjectivity = analyze_subjectivity(text)

    return {
        "emotion": emotion,
        "subjectivity": subjectivity
    }