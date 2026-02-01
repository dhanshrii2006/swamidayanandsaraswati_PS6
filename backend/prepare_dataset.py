"""
Dataset Preparation Script for Mistral-7B-Instruct Fine-tuning
Generates emergency extraction dataset in JSONL format
"""

import json
import random
from datetime import datetime


# ============================================================================
# TRAINING SAMPLES - Emergency Information Extraction
# ============================================================================

EMERGENCY_SAMPLES = [
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Car accident near highway exit 12, driver bleeding from head injury",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["bleeding", "head injury", "accident"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Vehicle caught fire, flames visible from engine, need fire department",
        "output": {
            "issue_type": "fire",
            "emergency_keywords": ["fire", "flames"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "My car has a flat tire on the side of the road",
        "output": {
            "issue_type": "flat_tire",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Car battery is completely dead, won't start at all",
        "output": {
            "issue_type": "battery_dead",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Serious collision on main street, multiple people injured, ambulance needed immediately",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["collision", "injured", "ambulance", "immediately", "serious"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Engine is making strange noise and overheating",
        "output": {
            "issue_type": "engine",
            "emergency_keywords": ["overheating"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Child locked inside car, doors won't open, child is crying",
        "output": {
            "issue_type": "trapped",
            "emergency_keywords": ["locked", "child", "trapped"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Minor fender bender in parking lot, no injuries, just scratches",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Thick black smoke coming from under hood, engine very hot",
        "output": {
            "issue_type": "engine",
            "emergency_keywords": ["smoke", "hot"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Pregnant woman in labor, need immediate medical assistance",
        "output": {
            "issue_type": "medical_emergency",
            "emergency_keywords": ["pregnant", "labor", "immediate", "medical"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Gas leak detected, strong smell of gasoline, dangerous situation",
        "output": {
            "issue_type": "gas_leak",
            "emergency_keywords": ["gas leak", "dangerous"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Vehicle stuck in rising flood water, water entering cabin",
        "output": {
            "issue_type": "flood",
            "emergency_keywords": ["flood", "stuck", "rising"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Need routine oil change and tire rotation",
        "output": {
            "issue_type": "maintenance",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Brakes failed completely, cannot stop the vehicle, moving downhill",
        "output": {
            "issue_type": "brake_failure",
            "emergency_keywords": ["failed", "cannot stop", "brakes"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Hit and run accident, victim unconscious and bleeding heavily",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["unconscious", "bleeding", "heavily", "victim"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Car rolled over into ditch, driver trapped inside with chest pain",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["rolled over", "trapped", "chest pain"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Windshield wipers stopped working in heavy rain",
        "output": {
            "issue_type": "electrical",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Person having heart attack in vehicle, need paramedics urgently",
        "output": {
            "issue_type": "medical_emergency",
            "emergency_keywords": ["heart attack", "paramedics", "urgently"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Steering wheel locked up, car veering off road dangerously",
        "output": {
            "issue_type": "steering_failure",
            "emergency_keywords": ["locked", "veering", "dangerously"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Tire burst on highway at high speed, car spinning out of control",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["burst", "spinning", "out of control"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Just need a jump start, battery seems weak",
        "output": {
            "issue_type": "battery_dead",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Airbags deployed after collision, driver has broken arm",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["airbags deployed", "collision", "broken arm"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Car making grinding noise when turning steering wheel",
        "output": {
            "issue_type": "steering",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Electrical fire in dashboard, sparks flying, smoke filling cabin",
        "output": {
            "issue_type": "fire",
            "emergency_keywords": ["fire", "sparks", "smoke"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Ran out of gas on rural road, no injuries",
        "output": {
            "issue_type": "out_of_gas",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Vehicle exploded after crash, severe burns on driver",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["exploded", "crash", "severe", "burns"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Keys locked inside car, baby sleeping in back seat",
        "output": {
            "issue_type": "lockout",
            "emergency_keywords": ["locked", "baby"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Coolant leak causing engine to overheat rapidly",
        "output": {
            "issue_type": "engine",
            "emergency_keywords": ["overheat", "rapidly"]
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Check engine light came on, car running normally",
        "output": {
            "issue_type": "engine",
            "emergency_keywords": []
        }
    },
    {
        "instruction": "Extract emergency information from the user's roadside assistance request. Return a JSON object with 'issue_type' and 'emergency_keywords' fields.",
        "input": "Multi-vehicle pileup on bridge, many injured, need multiple ambulances",
        "output": {
            "issue_type": "accident",
            "emergency_keywords": ["pileup", "injured", "ambulances", "multiple"]
        }
    }
]


# ============================================================================
# DATASET GENERATION FUNCTIONS
# ============================================================================

def format_mistral_instruction(sample):
    """
    Format sample in Mistral instruction format for training.
    Returns a dictionary with text field containing the full formatted prompt.
    """
    instruction = sample["instruction"]
    input_text = sample["input"]
    output = json.dumps(sample["output"], ensure_ascii=False)
    
    # Mistral instruction format
    formatted_text = f"<s>[INST] {instruction}\n\nUser input: {input_text} [/INST] {output}</s>"
    
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
        "text": formatted_text
    }


def save_to_jsonl(data, filename):
    """Save data to JSONL (JSON Lines) format."""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✅ Saved {len(data)} samples to {filename}")


def save_to_json(data, filename):
    """Save data to regular JSON format."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(data)} samples to {filename}")


def generate_dataset_stats(data):
    """Generate and print dataset statistics."""
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    
    print(f"Total samples: {len(data)}")
    
    # Count issue types
    issue_types = {}
    emergency_count = 0
    
    for sample in data:
        output = json.loads(sample["output"]) if isinstance(sample["output"], str) else sample["output"]
        issue_type = output.get("issue_type", "unknown")
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        if len(output.get("emergency_keywords", [])) > 0:
            emergency_count += 1
    
    print(f"\nEmergency cases: {emergency_count} ({emergency_count/len(data)*100:.1f}%)")
    print(f"Non-emergency cases: {len(data) - emergency_count} ({(len(data)-emergency_count)/len(data)*100:.1f}%)")
    
    print("\nIssue type distribution:")
    for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue_type}: {count} ({count/len(data)*100:.1f}%)")
    
    print("\n" + "=" * 60)


def create_train_test_split(data, test_ratio=0.2):
    """Split data into training and test sets."""
    random.shuffle(data)
    split_idx = int(len(data) * (1 - test_ratio))
    return data[:split_idx], data[split_idx:]


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Generate and save fine-tuning dataset."""
    
    print("=" * 60)
    print("EMERGENCY EXTRACTION DATASET PREPARATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: Mistral-7B-Instruct")
    print("=" * 60)
    
    # Format all samples
    print("\nFormatting samples...")
    formatted_data = [format_mistral_instruction(sample) for sample in EMERGENCY_SAMPLES]
    
    # Generate statistics
    generate_dataset_stats(formatted_data)
    
    # Split into train/test
    print("\nSplitting into train/test sets...")
    train_data, test_data = create_train_test_split(formatted_data.copy(), test_ratio=0.2)
    print(f"Training samples: {len(train_data)}")
    print(f"Test samples: {len(test_data)}")
    
    # Save datasets
    print("\nSaving datasets...")
    
    # Save as JSONL (recommended for training)
    save_to_jsonl(train_data, "emergency_train.jsonl")
    save_to_jsonl(test_data, "emergency_test.jsonl")
    save_to_jsonl(formatted_data, "emergency_full.jsonl")
    
    # Save as JSON (for inspection)
    save_to_json(train_data, "emergency_train.json")
    save_to_json(test_data, "emergency_test.json")
    
    # Print sample
    print("\n" + "=" * 60)
    print("SAMPLE FORMATTED RECORD")
    print("=" * 60)
    sample = formatted_data[0]
    print(f"Instruction: {sample['instruction'][:80]}...")
    print(f"Input: {sample['input']}")
    print(f"Output: {sample['output']}")
    print(f"\nFull formatted text:")
    print(sample['text'])
    
    print("\n" + "=" * 60)
    print("✅ DATASET PREPARATION COMPLETE")
    print("=" * 60)
    print("\nFiles created:")
    print("  - emergency_train.jsonl (training set)")
    print("  - emergency_test.jsonl (test set)")
    print("  - emergency_full.jsonl (complete dataset)")
    print("  - emergency_train.json (human-readable)")
    print("  - emergency_test.json (human-readable)")
    print("\nUse emergency_train.jsonl for fine-tuning!")


if __name__ == "__main__":
    main()
