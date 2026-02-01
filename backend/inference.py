"""
Inference Script for Fine-tuned Mistral-7B-Instruct Emergency Extraction Model

Loads base model + LoRA adapter and runs inference on user text.
Usage:
    python inference.py
    python inference.py --text "Your custom input text"
    python inference.py --interactive
"""

import torch
import argparse
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from strict_json_prompts import get_recommended_prompt, extract_json_from_response


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
LORA_ADAPTER_PATH = "./emergency_lora_model"  # Path to fine-tuned LoRA weights

# 4-bit quantization config (matches training)
QUANTIZATION_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

# Generation parameters
GENERATION_CONFIG = {
    "max_new_tokens": 200,
    "temperature": 0.1,
    "do_sample": True,
    "top_p": 0.95,
    "top_k": 50,
    "repetition_penalty": 1.1,
}


# ============================================================================
# MODEL LOADING
# ============================================================================

class EmergencyExtractor:
    """Wrapper class for emergency information extraction."""
    
    def __init__(self, base_model_name=BASE_MODEL, lora_path=LORA_ADAPTER_PATH, use_lora=True):
        """
        Initialize the model.
        
        Args:
            base_model_name: HuggingFace model ID
            lora_path: Path to LoRA adapter weights
            use_lora: Whether to load LoRA adapter (False = base model only)
        """
        print("=" * 70)
        print("LOADING MODEL")
        print("=" * 70)
        
        # Load tokenizer
        print(f"Loading tokenizer from {base_model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model with 4-bit quantization
        print(f"Loading base model from {base_model_name} (4-bit quantization)...")
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config=QUANTIZATION_CONFIG,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        
        # Load LoRA adapter if available
        if use_lora:
            try:
                print(f"Loading LoRA adapter from {lora_path}...")
                self.model = PeftModel.from_pretrained(self.model, lora_path)
                print("✓ LoRA adapter loaded successfully")
            except Exception as e:
                print(f"⚠ Could not load LoRA adapter: {e}")
                print("⚠ Using base model only")
        
        self.model.eval()
        print("✓ Model ready for inference")
        print()
    
    def extract(self, user_text, return_raw=False):
        """
        Extract emergency information from user text.
        
        Args:
            user_text: User's description of their issue
            return_raw: If True, return raw model output; if False, return parsed JSON
        
        Returns:
            dict: Extracted emergency information or raw string if return_raw=True
        """
        # Create prompt using strict JSON template
        prompt = get_recommended_prompt(user_text)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **GENERATION_CONFIG
            )
        
        # Decode
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the model's response (remove the prompt)
        # Mistral format: <s>[INST] prompt [/INST] response
        if "[/INST]" in full_response:
            model_output = full_response.split("[/INST]")[-1].strip()
        else:
            model_output = full_response
        
        if return_raw:
            return model_output
        
        # Parse JSON from response
        result = extract_json_from_response(model_output)
        return result


# ============================================================================
# INFERENCE FUNCTIONS
# ============================================================================

def run_single_inference(extractor, text):
    """Run inference on a single text input."""
    print("=" * 70)
    print("INFERENCE")
    print("=" * 70)
    print(f"Input: {text}\n")
    
    # Get raw output
    raw_output = extractor.extract(text, return_raw=True)
    print(f"Raw Model Output:\n{raw_output}\n")
    
    # Get parsed JSON
    parsed_result = extractor.extract(text, return_raw=False)
    print(f"Parsed JSON:")
    print(json.dumps(parsed_result, indent=2))
    print()
    
    return parsed_result


def run_interactive_mode(extractor):
    """Interactive mode - keep asking for input."""
    print("=" * 70)
    print("INTERACTIVE MODE")
    print("=" * 70)
    print("Enter text to extract emergency information.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            user_input = input("Your input: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                print("Please enter some text.\n")
                continue
            
            print()
            result = run_single_inference(extractor, user_input)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def run_batch_test(extractor):
    """Run inference on a batch of test examples."""
    test_examples = [
        "Car accident on highway 101, multiple injuries, ambulance needed",
        "My car battery is dead, need jump start",
        "Flat tire on I-95, have spare but no jack",
        "Engine fire! Smoke coming from hood, pulled over safely",
        "Brake failure while driving, very dangerous situation",
        "Out of gas near exit 23",
    ]
    
    print("=" * 70)
    print("BATCH TEST MODE")
    print("=" * 70)
    print(f"Running inference on {len(test_examples)} examples...\n")
    
    results = []
    for i, example in enumerate(test_examples, 1):
        print(f"\n--- Example {i}/{len(test_examples)} ---")
        result = run_single_inference(extractor, example)
        results.append({
            "input": example,
            "output": result
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("BATCH TEST SUMMARY")
    print("=" * 70)
    
    emergency_count = 0
    for i, r in enumerate(results, 1):
        issue_type = r["output"].get("issue_type", "unknown")
        keywords = r["output"].get("emergency_keywords", [])
        is_emergency = len(keywords) > 0
        
        if is_emergency:
            emergency_count += 1
        
        status = "🚨 EMERGENCY" if is_emergency else "✓ Standard"
        print(f"{i}. {status:15} | {issue_type:20} | {len(keywords)} keywords")
    
    print(f"\nEmergency cases: {emergency_count}/{len(test_examples)}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run inference on fine-tuned Mistral-7B emergency extraction model"
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Input text for inference"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Run batch test on predefined examples"
    )
    parser.add_argument(
        "--base-only",
        action="store_true",
        help="Use base model only (skip LoRA adapter)"
    )
    parser.add_argument(
        "--lora-path",
        type=str,
        default=LORA_ADAPTER_PATH,
        help="Path to LoRA adapter weights"
    )
    
    args = parser.parse_args()
    
    # Load model
    try:
        extractor = EmergencyExtractor(
            lora_path=args.lora_path,
            use_lora=not args.base_only
        )
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    # Run inference based on mode
    if args.batch:
        run_batch_test(extractor)
    elif args.interactive:
        run_interactive_mode(extractor)
    elif args.text:
        run_single_inference(extractor, args.text)
    else:
        # Default: run a single example
        default_text = "Car accident with injuries, need help immediately"
        print("No input provided. Running default example...\n")
        run_single_inference(extractor, default_text)
        print("\nTip: Use --help to see all options")


if __name__ == "__main__":
    main()
