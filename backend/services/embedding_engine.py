# Path: intelligent_summarizer/backend/services/embedding_engine.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load model once (very important)
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    return model.encode(text)

def calculate_similarity(text1, text2):
    embedding1 = get_embedding(text1)
    embedding2 = get_embedding(text2)

    similarity_score = cosine_similarity(
        [embedding1],
        [embedding2]
    )[0][0]

    return float(similarity_score)
