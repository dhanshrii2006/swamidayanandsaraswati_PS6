# Quick Start Guide: Running Inference

## Basic Usage

```bash
# Single inference (default example)
python inference.py

# Custom text
python inference.py --text "Car on fire, need help now!"

# Interactive mode
python inference.py --interactive

# Batch test (6 predefined examples)
python inference.py --batch

# Use base model only (without LoRA)
python inference.py --base-only
```

## Requirements

Before running, ensure ML dependencies are installed:

```bash
pip install -r requirements_ml.txt
```

Or install manually:
```bash
pip install torch transformers peft bitsandbytes accelerate
```

## Expected Output

```
======================================================================
LOADING MODEL
======================================================================
Loading tokenizer from mistralai/Mistral-7B-Instruct-v0.1...
Loading base model from mistralai/Mistral-7B-Instruct-v0.1 (4-bit quantization)...
Loading LoRA adapter from ./emergency_lora_model...
✓ LoRA adapter loaded successfully
✓ Model ready for inference

======================================================================
INFERENCE
======================================================================
Input: Car accident with injuries, need help immediately

Raw Model Output:
{"issue_type": "accident", "emergency_keywords": ["accident", "injuries"]}

Parsed JSON:
{
  "issue_type": "accident",
  "emergency_keywords": [
    "accident",
    "injuries"
  ]
}
```

## Troubleshooting

### LoRA adapter not found
If you haven't trained the model yet:
```bash
python inference.py --base-only
```

This will use the base Mistral model without fine-tuning.

### Out of memory
The script uses 4-bit quantization to reduce memory usage. If you still get OOM errors:
- Close other GPU applications
- Reduce `max_new_tokens` in GENERATION_CONFIG
- Use a machine with more GPU RAM (requires ~10GB)

### CUDA not available
The script will automatically fall back to CPU, but inference will be slower.

## Integration with API

To use this in your Flask API, see [ml_emergency_integration.py](ml_emergency_integration.py) for a complete integration example.
