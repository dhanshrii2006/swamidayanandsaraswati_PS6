"""
Fine-tune Mistral-7B-Instruct using QLoRA for Emergency Information Extraction
Trains model to extract structured emergency data from roadside assistance requests
"""

import os
import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    PeftModel
)
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
OUTPUT_DIR = "./emergency_model_output"
LORA_OUTPUT_DIR = "./emergency_lora_model"

# LoRA Configuration
LORA_R = 16  # LoRA rank
LORA_ALPHA = 32  # LoRA alpha
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

# Training Configuration
MAX_LENGTH = 512
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
WARMUP_STEPS = 100


# ============================================================================
# TRAINING DATA - Emergency Extraction Examples
# ============================================================================

TRAINING_DATA = [
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Car accident near flyover, person bleeding",
        "output": json.dumps({
            "issue_type": "accident",
            "emergency_keywords": ["bleeding", "accident"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "My car broke down with engine smoke",
        "output": json.dumps({
            "issue_type": "engine",
            "emergency_keywords": ["smoke"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Flat tire on highway",
        "output": json.dumps({
            "issue_type": "flat_tire",
            "emergency_keywords": []
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Battery dead, need jump start",
        "output": json.dumps({
            "issue_type": "battery_dead",
            "emergency_keywords": []
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Serious accident, multiple injuries, need ambulance urgently",
        "output": json.dumps({
            "issue_type": "accident",
            "emergency_keywords": ["injuries", "ambulance", "urgently", "serious"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Car caught fire, flames visible",
        "output": json.dumps({
            "issue_type": "fire",
            "emergency_keywords": ["fire", "flames"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Vehicle rolled over, driver unconscious",
        "output": json.dumps({
            "issue_type": "accident",
            "emergency_keywords": ["unconscious", "rolled over"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Minor fender bender, no injuries",
        "output": json.dumps({
            "issue_type": "accident",
            "emergency_keywords": []
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Engine overheating badly, smoke coming out",
        "output": json.dumps({
            "issue_type": "engine",
            "emergency_keywords": ["smoke", "overheating"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Child trapped in car, doors won't open",
        "output": json.dumps({
            "issue_type": "trapped",
            "emergency_keywords": ["trapped", "child"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Head-on collision, severe injuries, multiple casualties",
        "output": json.dumps({
            "issue_type": "accident",
            "emergency_keywords": ["collision", "severe", "injuries", "casualties"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Tire burst on highway causing accident",
        "output": json.dumps({
            "issue_type": "accident",
            "emergency_keywords": ["accident"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Need tow truck, car won't start",
        "output": json.dumps({
            "issue_type": "engine",
            "emergency_keywords": []
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Person having heart attack in car, need immediate help",
        "output": json.dumps({
            "issue_type": "medical_emergency",
            "emergency_keywords": ["heart attack", "immediate"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Gas leak from vehicle, danger of explosion",
        "output": json.dumps({
            "issue_type": "gas_leak",
            "emergency_keywords": ["gas leak", "explosion", "danger"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Pregnant woman in labor in car",
        "output": json.dumps({
            "issue_type": "medical_emergency",
            "emergency_keywords": ["pregnant", "labor"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Vehicle stuck in flood water rising",
        "output": json.dumps({
            "issue_type": "flood",
            "emergency_keywords": ["flood", "stuck", "rising"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Just need oil change service",
        "output": json.dumps({
            "issue_type": "maintenance",
            "emergency_keywords": []
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Brakes failed completely, can't stop the car",
        "output": json.dumps({
            "issue_type": "brake_failure",
            "emergency_keywords": ["failed", "can't stop"]
        })
    },
    {
        "instruction": "Extract emergency information from the text and return JSON with issue_type and emergency_keywords.",
        "input": "Hit and run accident, victim bleeding heavily",
        "output": json.dumps({
            "issue_type": "accident",
            "emergency_keywords": ["bleeding", "heavily", "victim"]
        })
    }
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_prompt(instruction, input_text):
    """Format prompt in Mistral instruction format."""
    return f"<s>[INST] {instruction}\n\nUser input: {input_text} [/INST]"


def format_training_example(example):
    """Format a complete training example with instruction, input, and output."""
    prompt = format_prompt(example["instruction"], example["input"])
    return f"{prompt} {example['output']}</s>"


def create_dataset(data):
    """Create HuggingFace Dataset from training data."""
    formatted_data = []
    for item in data:
        formatted_text = format_training_example(item)
        formatted_data.append({"text": formatted_text})
    
    return Dataset.from_list(formatted_data)


# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model_and_tokenizer():
    """Load model with 4-bit quantization and tokenizer."""
    
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    print("Configuring 4-bit quantization...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    print(f"Loading model: {MODEL_NAME}")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    print("Preparing model for k-bit training...")
    model = prepare_model_for_kbit_training(model)
    
    return model, tokenizer


def setup_lora(model):
    """Configure and apply LoRA to the model."""
    
    print("Configuring LoRA...")
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    print("Applying LoRA adapters...")
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
    
    return model


# ============================================================================
# DATA PREPROCESSING
# ============================================================================

def tokenize_function(examples, tokenizer):
    """Tokenize the text data."""
    result = tokenizer(
        examples["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding="max_length",
    )
    result["labels"] = result["input_ids"].copy()
    return result


# ============================================================================
# TRAINING
# ============================================================================

def train_model():
    """Main training function."""
    
    print("=" * 80)
    print("EMERGENCY INFORMATION EXTRACTION MODEL TRAINING")
    print("=" * 80)
    
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer()
    
    # Setup LoRA
    model = setup_lora(model)
    
    # Prepare dataset
    print("\nPreparing training dataset...")
    train_dataset = create_dataset(TRAINING_DATA)
    print(f"Training examples: {len(train_dataset)}")
    
    # Tokenize dataset
    print("Tokenizing dataset...")
    tokenized_dataset = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=train_dataset.column_names
    )
    
    # Training arguments
    print("\nConfiguring training arguments...")
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        num_train_epochs=NUM_EPOCHS,
        warmup_steps=WARMUP_STEPS,
        logging_steps=10,
        save_strategy="epoch",
        fp16=True,
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        gradient_checkpointing=True,
        report_to="none",
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Initialize trainer
    print("\nInitializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    
    # Train
    print("\n" + "=" * 80)
    print("STARTING TRAINING")
    print("=" * 80)
    trainer.train()
    
    # Save model
    print("\nSaving LoRA adapters...")
    model.save_pretrained(LORA_OUTPUT_DIR)
    tokenizer.save_pretrained(LORA_OUTPUT_DIR)
    
    print(f"\n✅ Training complete! Model saved to: {LORA_OUTPUT_DIR}")
    
    return model, tokenizer


# ============================================================================
# INFERENCE
# ============================================================================

def test_model(model, tokenizer, test_inputs):
    """Test the trained model on sample inputs."""
    
    print("\n" + "=" * 80)
    print("TESTING TRAINED MODEL")
    print("=" * 80)
    
    model.eval()
    
    for test_input in test_inputs:
        print(f"\n📝 Input: {test_input}")
        
        instruction = "Extract emergency information from the text and return JSON with issue_type and emergency_keywords."
        prompt = format_prompt(instruction, test_input)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.1,
                do_sample=True,
                top_p=0.95,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the JSON output
        if "[/INST]" in response:
            output = response.split("[/INST]")[-1].strip()
            print(f"🤖 Output: {output}")
        else:
            print(f"🤖 Full response: {response}")


def load_trained_model_for_inference():
    """Load the trained LoRA model for inference."""
    
    print("Loading base model...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    
    print("Loading LoRA adapters...")
    model = PeftModel.from_pretrained(base_model, LORA_OUTPUT_DIR)
    
    return model, tokenizer


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Check for required packages
    try:
        import bitsandbytes
        import peft
        import transformers
    except ImportError as e:
        print("❌ Missing required packages!")
        print("\nInstall with:")
        print("pip install transformers peft bitsandbytes accelerate datasets")
        sys.exit(1)
    
    # Check GPU availability
    if not torch.cuda.is_available():
        print("⚠️  Warning: No GPU detected! Training will be very slow on CPU.")
        print("Consider using Google Colab or a machine with GPU.")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != "yes":
            sys.exit(1)
    else:
        print(f"✅ GPU detected: {torch.cuda.get_device_name(0)}")
    
    # Train model
    model, tokenizer = train_model()
    
    # Test on sample inputs
    test_inputs = [
        "Car crash with multiple injuries",
        "Battery is dead",
        "Vehicle on fire, flames everywhere",
        "Tire puncture on highway"
    ]
    
    test_model(model, tokenizer, test_inputs)
    
    print("\n" + "=" * 80)
    print("✅ ALL DONE!")
    print("=" * 80)
    print(f"\nTrained model saved to: {LORA_OUTPUT_DIR}")
    print("\nTo use the model:")
    print("1. Load with: load_trained_model_for_inference()")
    print("2. Or integrate into your roadside assistance API")
