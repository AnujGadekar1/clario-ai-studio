# Path: intelligent_summarizer/backend/services/analysis.py

import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import textstat
from textblob import TextBlob
from services.emotion_service import analyze_emotion

# ---------------------------------------------------
# MODEL LOADING (Load once only)
# ---------------------------------------------------

# Use lighter model for production stability
# Change to "en_core_web_trf" only if you REALLY need transformer accuracy
nlp = spacy.load("en_core_web_sm")

analyzer = SentimentIntensityAnalyzer()


# ---------------------------------------------------
# SUBJECTIVITY (Keep here)
# Emotion removed (now handled by emotion_service.py)
# ---------------------------------------------------

def analyze_subjectivity(text: str):
    if not text.strip():
        return {"subjectivity_score": 0.0, "type": "objective"}

    blob = TextBlob(text)
    score = blob.sentiment.subjectivity

    return {
        "subjectivity_score": round(score, 3),
        "type": "subjective" if score > 0.5 else "objective"
    }


# ---------------------------------------------------
# MAIN ANALYSIS FUNCTION
# ---------------------------------------------------

def analyze_text(text: str):

    if not text.strip():
        return {
            "entities": [],
            "keywords": [],
            "sentiment": {},
            "subjectivity": {},
            "readability": {}
        }

    # 🔒 Limit text length for safety (important for large PDFs)
    text = text[:5000]

    doc = nlp(text)

    # -------------------------
    # Entities
    # -------------------------
    allowed_labels = {"PERSON", "ORG", "GPE", "PRODUCT", "EVENT"}

    entities = []
    seen = set()

    for ent in doc.ents:
        if ent.label_ in allowed_labels and len(ent.text) > 2:
            key = (ent.text.strip(), ent.label_)
            if key not in seen:
                entities.append(key)
                seen.add(key)

    entities = entities[:12]

    # -------------------------
    # Keywords (noun chunks)
    # -------------------------
    keywords = []
    seen_keywords = set()

    for chunk in doc.noun_chunks:
        cleaned = chunk.text.lower().strip()

        if (
            len(cleaned) > 4
            and not any(char.isdigit() for char in cleaned)
            and cleaned not in seen_keywords
        ):
            keywords.append(cleaned)
            seen_keywords.add(cleaned)

        if len(keywords) >= 8:
            break

    # -------------------------
    # Sentiment (VADER)
    # -------------------------
    sentiment = analyzer.polarity_scores(text)

    # -------------------------
    # Readability
    # -------------------------
    readability = {
        "flesch_reading_ease": round(textstat.flesch_reading_ease(text), 2),
        "grade_level": textstat.text_standard(text)
    }

    # -------------------------
    # Subjectivity
    # -------------------------
    subjectivity = analyze_subjectivity(text)
    emotion = analyze_emotion(text)

    return {
        "entities": entities,
        "keywords": keywords,
        "sentiment": sentiment,
        "emotion": emotion,   
        "subjectivity": subjectivity,
        "readability": readability
}