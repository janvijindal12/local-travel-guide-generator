from __future__ import annotations

import os

from dotenv import load_dotenv

from app.core import build_prompt, find_sample_guide

load_dotenv()


def generate_guide(destination: str, interests: str) -> tuple[str, str]:
    mode = os.getenv("TRAVEL_GUIDE_MODE", "sample").strip().lower()
    if mode == "groq":
        return _generate_with_groq(destination, interests), "Groq hosted model"
    if mode == "merged":
        return _generate_with_transformers(destination, interests), "Merged local model"
    sample = find_sample_guide(destination, interests)
    if sample:
        return sample, "Sample guide"
    return (
        "I don't have a matching sample for that combination yet. Try Porto with food, "
        "architecture, or waterfront interests, or configure a model in your environment.",
        "Sample guide",
    )


def _generate_with_groq(destination: str, interests: str) -> str:
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Add GROQ_API_KEY to your .env file before using Groq mode.")
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        messages=[{"role": "user", "content": build_prompt(destination, interests)}],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content or "The model returned an empty guide."


def _generate_with_transformers(destination: str, interests: str) -> str:
    from transformers import pipeline

    model_path = os.getenv("MERGED_MODEL_DIR", "artifacts/merged-model")
    generator = pipeline("text-generation", model=model_path, tokenizer=model_path)
    result = generator(build_prompt(destination, interests), max_new_tokens=180, do_sample=True, temperature=0.7)
    return result[0]["generated_text"]
