"""
Lightweight CPU-Compatible Training Script
Alternative to full QLoRA training - uses smaller model and standard fine-tuning
"""

import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset

# Use smaller model for CPU training
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Much smaller than Mistral-7B
OUTPUT_DIR = "./emergency_model_cpu"

# Reduced training config for CPU
MAX_LENGTH = 256
BATCH_SIZE = 1
NUM_EPOCHS = 2
LEARNING_RATE = 5e-5

# Same training data
TRAINING_DATA = [
    {
        "instruction": "Extract emergency info",
        "input": "Car accident, person bleeding",
        "output": json.dumps({"issue_type": "accident", "emergency_keywords": ["bleeding"]})
    },
    {
        "instruction": "Extract emergency info",
        "input": "Engine smoke",
        "output": json.dumps({"issue_type": "engine", "emergency_keywords": ["smoke"]})
    },
    {
        "instruction": "Extract emergency info",
        "input": "Flat tire",
        "output": json.dumps({"issue_type": "flat_tire", "emergency_keywords": []})
    },
    {
        "instruction": "Extract emergency info",
        "input": "Battery dead",
        "output": json.dumps({"issue_type": "battery_dead", "emergency_keywords": []})
    },
    {
        "instruction": "Extract emergency info",
        "input": "Serious accident, multiple injuries",
        "output": json.dumps({"issue_type": "accident", "emergency_keywords": ["injuries", "serious"]})
    },
]


def format_example(item):
    return f"<|user|>\n{item['instruction']}: {item['input']}<|assistant|>\n{item['output']}<|end|>"


def train_cpu_model():
    print("Loading tokenizer and model (CPU mode)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)
    
    print("Preparing dataset...")
    dataset = Dataset.from_list([{"text": format_example(item)} for item in TRAINING_DATA])
    
    def tokenize(examples):
        result = tokenizer(examples["text"], truncation=True, max_length=MAX_LENGTH, padding="max_length")
        result["labels"] = result["input_ids"].copy()
        return result
    
    tokenized = dataset.map(tokenize, batched=True, remove_columns=["text"])
    
    print("Training...")
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LEARNING_RATE,
        logging_steps=1,
        save_strategy="epoch",
    )
    
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )
    
    trainer.train()
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"✅ Model saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    print("⚠️  CPU Training Mode - This will be slow!")
    train_cpu_model()
