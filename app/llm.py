from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from app.core import build_prompt, find_sample_guide

load_dotenv()


NO_MATCH = "I don't have a guide for that combination yet. Try another interest, or add a reviewed example to the local dataset."


def generate_guide(destination: str, interests: str) -> tuple[str, str]:
    mode = os.getenv("TRAVEL_GUIDE_MODE", "sample").strip().lower()
    if mode == "groq":
        return _generate_with_groq(destination, interests), "Groq hosted model"
    if mode == "merged":
        return _generate_with_transformers(destination, interests), "Merged local model"
    guide = find_sample_guide(destination, interests)
    return (guide or NO_MATCH), "Curated sample"


def _generate_with_groq(destination: str, interests: str) -> str:
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Add GROQ_API_KEY to your .env file before using Groq mode.")
    response = Groq(api_key=api_key).chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        messages=[{"role": "user", "content": build_prompt(destination, interests)}],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content or "The model returned an empty guide."


def _generate_with_transformers(destination: str, interests: str) -> str:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_path = Path(os.getenv("MERGED_MODEL_DIR", "artifacts/merged-model"))
    if not model_path.exists():
        raise FileNotFoundError(f"No merged model found at {model_path}. Train and merge an adapter first.")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    inputs = tokenizer(build_prompt(destination, interests), return_tensors="pt")
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=120, do_sample=True, temperature=0.7, pad_token_id=tokenizer.eos_token_id)
    return tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
