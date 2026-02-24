# Path: intelligent_summarizer/backend/services/rag_engine.py

import faiss
import numpy as np
import os
import pickle
from services.embedding_engine import model
from services.neural_refiner import generate_llm_answer

INDEX_PATH = "rag_index.faiss"
CHUNKS_PATH = "rag_chunks.pkl"


class RAGEngine:

    def __init__(self):
        self.index = None
        self.chunks = []
        self.load_index()

    def split_text(self, text, chunk_size=200, overlap=50):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def build_index(self, text):
        self.chunks = self.split_text(text)

        if not self.chunks:
            return

        embeddings = model.encode(self.chunks)
        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings))

        self.save_index()

    async def query(self, question, top_k=3):

        if self.index is None:
            return "RAG index not built."

        question_embedding = model.encode([question])

        distances, indices = self.index.search(
            np.array(question_embedding),
            min(top_k, len(self.chunks))
        )

        retrieved_chunks = [
            self.chunks[i] for i in indices[0] if i < len(self.chunks)
        ]

        context = "\n".join(retrieved_chunks)

        answer = await generate_llm_answer(question, context)

        return answer

    def save_index(self):
        if self.index:
            faiss.write_index(self.index, INDEX_PATH)
            with open(CHUNKS_PATH, "wb") as f:
                pickle.dump(self.chunks, f)

    def load_index(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(CHUNKS_PATH, "rb") as f:
                self.chunks = pickle.load(f)


rag_engine = RAGEngine()
