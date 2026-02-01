# Emergency Model Training Guide

## 🚀 Quick Start

### 1. Install ML Dependencies

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Install PyTorch with CUDA (if you have GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install ML packages
pip install -r requirements_ml.txt
```

### 2. Run Training

```powershell
E:/new/backend/venv/Scripts/python.exe train_emergency_model.py
```

---

## 📋 What This Does

Trains Mistral-7B to extract emergency information from text:

**Input:** "Car accident near flyover, person bleeding"

**Output:**
```json
{
  "issue_type": "accident",
  "emergency_keywords": ["bleeding", "accident"]
}
```

---

## ⚙️ Configuration

Edit these in `train_emergency_model.py`:

```python
# LoRA Settings
LORA_R = 16              # Rank (higher = more parameters)
LORA_ALPHA = 32          # Scaling factor
LORA_DROPOUT = 0.05      # Dropout rate

# Training Settings
BATCH_SIZE = 4           # Batch size per GPU
NUM_EPOCHS = 3           # Training epochs
LEARNING_RATE = 2e-4     # Learning rate
MAX_LENGTH = 512         # Max token length
```

---

## 💾 Model Output

After training, model saved to:
- **LoRA adapters:** `./emergency_lora_model/`
- **Checkpoints:** `./emergency_model_output/`

---

## 🧪 Testing the Model

The script automatically tests on sample inputs after training:

```python
test_inputs = [
    "Car crash with multiple injuries",
    "Battery is dead",
    "Vehicle on fire, flames everywhere",
    "Tire puncture on highway"
]
```

---

## 🔗 Integration with API

### Option 1: Replace emergency_scoring.py

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import json

# Load model once at startup
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.1",
    load_in_4bit=True,
    device_map="auto"
)
model = PeftModel.from_pretrained(base_model, "./emergency_lora_model")

def calculate_emergency_score(data):
    text = data.get("description", "")
    
    prompt = f"<s>[INST] Extract emergency information from the text and return JSON with issue_type and emergency_keywords.\n\nUser input: {text} [/INST]"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=150)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Parse JSON from response
    json_str = response.split("[/INST]")[-1].strip()
    result = json.loads(json_str)
    
    # Calculate score based on keywords
    score = 0
    if result["issue_type"] == "accident":
        score += 60
    score += len(result["emergency_keywords"]) * 15
    score = min(score, 100)
    
    return {
        "emergency_score": score,
        "emergency_flag": score >= 70,
        "issue_type": result["issue_type"],
        "emergency_keywords": result["emergency_keywords"]
    }
```

### Option 2: Add as separate endpoint

Add to `api.py`:

```python
from train_emergency_model import load_trained_model_for_inference

# Load model at startup
ml_model, ml_tokenizer = load_trained_model_for_inference()

@app.route('/api/extract-emergency', methods=['POST'])
def extract_emergency():
    data = request.get_json()
    text = data.get('text', '')
    
    # Use model for extraction
    # ... (inference code)
    
    return jsonify(result)
```

---

## 📊 Training Data

Currently includes **20 examples** covering:
- Accidents (various severity)
- Medical emergencies
- Fire/gas leaks
- Brake failures
- Trapped situations
- Normal maintenance

**To improve:** Add more real-world examples to `TRAINING_DATA` list

---

## 🎯 Expected Results

After 3 epochs on 20 examples:
- Model learns emergency patterns
- Extracts issue types accurately
- Identifies emergency keywords
- Outputs valid JSON

For production, train on 1000+ examples!

---

## ⚠️ Requirements

- **GPU:** Recommended (training takes 10-30 min)
- **RAM:** 16GB+ 
- **VRAM:** 8GB+ GPU memory
- **Disk:** 15GB for model

**No GPU?** Training will be VERY slow (hours instead of minutes)

---

## 🐛 Troubleshooting

### CUDA Out of Memory
```python
BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 8
```

### Model not loading
```powershell
# Clear cache
python -c "import torch; torch.cuda.empty_cache()"
```

### Import errors
```powershell
pip install --upgrade transformers peft bitsandbytes
```

---

## 📈 Next Steps

1. **Collect more data** - Get real roadside assistance texts
2. **Evaluate accuracy** - Test on validation set
3. **Deploy** - Integrate into API
4. **Monitor** - Track prediction quality
5. **Retrain** - Update with new examples regularly
