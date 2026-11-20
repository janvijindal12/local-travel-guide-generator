import os
from pathlib import Path

from dotenv import load_dotenv
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

load_dotenv()


def main() -> None:
    base_id = os.getenv("BASE_MODEL_ID", "gpt2")
    adapter_dir = Path(os.getenv("TRAINING_OUTPUT_DIR", "artifacts/lora-adapter"))
    merged_dir = Path(os.getenv("MERGED_MODEL_DIR", "artifacts/merged-model"))
    if not adapter_dir.exists():
        raise FileNotFoundError(f"No LoRA adapter found at {adapter_dir}. Run python -m app.train first.")
    base = AutoModelForCausalLM.from_pretrained(base_id)
    tuned = PeftModel.from_pretrained(base, adapter_dir)
    merged_dir.mkdir(parents=True, exist_ok=True)
    tuned.merge_and_unload().save_pretrained(merged_dir, safe_serialization=True)
    AutoTokenizer.from_pretrained(base_id).save_pretrained(merged_dir)
    print(f"Saved merged model to {merged_dir}")


if __name__ == "__main__":
    main()
