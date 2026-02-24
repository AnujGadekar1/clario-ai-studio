# Path: intelligent_summarizer/backend/services/neural_refiner.py

import os
import asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = None

if api_key:
    client = genai.Client(api_key=api_key)


async def neural_coherence_refinement(summary_text: str) -> str:
    if not summary_text.strip():
        return summary_text

    if not client:
        return summary_text  # fallback if no API key

    prompt = f"""
Rewrite the following into a clean professional executive summary.
No headings. 1-2 paragraphs. Maintain technical accuracy.

Summary:
{summary_text}
"""

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.candidates[0].content.parts[0].text.strip()

    except Exception:
        return summary_text


async def generate_llm_answer(question: str, context: str) -> str:
    if not context.strip():
        return "No relevant context available."

    if not client:
        return "LLM unavailable."

    prompt = f"""
Answer strictly using provided context.
If not found say: Information not available.

Context:
{context}

Question:
{question}
"""

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.candidates[0].content.parts[0].text.strip()

    except Exception:
        return "Error generating answer."
