from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "guides.jsonl"


def main() -> None:
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

    model_id = os.getenv("BASE_MODEL_ID", "gpt2")
    output_dir = Path(os.getenv("TRAINING_OUTPUT_DIR", "artifacts/lora-adapter"))
    rows = [json.loads(line) for line in DATA_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    texts = [f"Traveler interests: {row['interests']}\nDestination: {row['destination']}\nGuide: {row['guide']}" for row in rows]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id)
    model.config.pad_token_id = tokenizer.eos_token_id
    model = get_peft_model(model, LoraConfig(task_type=TaskType.CAUSAL_LM, r=8, lora_alpha=16, lora_dropout=0.05, target_modules=["c_attn"]))
    dataset = Dataset.from_dict({"text": texts})

    def tokenize(batch):
        encoded = tokenizer(batch["text"], truncation=True, padding="max_length", max_length=256)
        encoded["labels"] = [ids[:] for ids in encoded["input_ids"]]
        return encoded

    tokenized = dataset.map(tokenize, batched=True, remove_columns=["text"])
    trainer = Trainer(model=model, args=TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=8,
        per_device_train_batch_size=2,
        learning_rate=2e-4,
        logging_steps=1,
        save_strategy="epoch",
        report_to="none",
    ), train_dataset=tokenized)
    trainer.train()
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Saved LoRA adapter to {output_dir}")


if __name__ == "__main__":
    main()
