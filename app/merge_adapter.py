import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    base_id = os.getenv("BASE_MODEL_ID", "gpt2")
    adapter_dir = Path(os.getenv("TRAINING_OUTPUT_DIR", "artifacts/lora-adapter"))
    merged_dir = Path(os.getenv("MERGED_MODEL_DIR", "artifacts/merged-model"))
    base = AutoModelForCausalLM.from_pretrained(base_id)
    tuned = PeftModel.from_pretrained(base, adapter_dir)
    merged = tuned.merge_and_unload()
    merged_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(merged_dir, safe_serialization=True)
    AutoTokenizer.from_pretrained(base_id).save_pretrained(merged_dir)
    print(f"Saved merged model to {merged_dir}")


if __name__ == "__main__":
    main()
