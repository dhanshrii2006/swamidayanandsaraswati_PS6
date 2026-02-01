# Dataset Preparation - Complete ✅

## 📊 Generated Files

Successfully created **5 dataset files**:

### JSONL Format (For Training)
1. **emergency_train.jsonl** - 24 training samples
2. **emergency_test.jsonl** - 6 test samples  
3. **emergency_full.jsonl** - 30 complete dataset

### JSON Format (For Inspection)
4. **emergency_train.json** - Human-readable training data
5. **emergency_test.json** - Human-readable test data

---

## 📈 Dataset Statistics

```
Total samples: 30
Emergency cases: 21 (70.0%)
Non-emergency cases: 9 (30.0%)

Issue types:
  - accident: 9 samples
  - engine: 4 samples
  - fire: 2 samples
  - battery_dead: 2 samples
  - medical_emergency: 2 samples
  - 11 other types: 1 sample each
```

---

## 📝 Record Format

Each record contains:

```json
{
  "instruction": "Extract emergency information from the user's roadside assistance request...",
  "input": "Car accident near highway exit 12, driver bleeding",
  "output": "{\"issue_type\": \"accident\", \"emergency_keywords\": [\"bleeding\", \"accident\"]}",
  "text": "<s>[INST] Extract emergency... [/INST] {...}</s>"
}
```

- **instruction**: Task description
- **input**: User's text
- **output**: JSON string with issue_type and emergency_keywords
- **text**: Full Mistral-formatted prompt for training

---

## 🚀 Usage

### For QLoRA Training

Use the **JSONL files** with the training script:

```python
from datasets import load_dataset

dataset = load_dataset('json', data_files='emergency_train.jsonl')
```

### For Standard Fine-tuning

```python
import json

with open('emergency_train.jsonl', 'r') as f:
    train_data = [json.loads(line) for line in f]
```

---

## ✏️ Adding More Data

Edit `prepare_dataset.py` and add to `EMERGENCY_SAMPLES`:

```python
{
    "instruction": "Extract emergency information...",
    "input": "Your new example text here",
    "output": {
        "issue_type": "your_type",
        "emergency_keywords": ["keyword1", "keyword2"]
    }
}
```

Then run:
```powershell
python prepare_dataset.py
```

---

## 📋 Sample Records

### Emergency Example
```json
{
  "input": "Car accident, driver bleeding from head injury",
  "output": {
    "issue_type": "accident",
    "emergency_keywords": ["bleeding", "head injury", "accident"]
  }
}
```

### Non-Emergency Example
```json
{
  "input": "Flat tire on the side of the road",
  "output": {
    "issue_type": "flat_tire",
    "emergency_keywords": []
  }
}
```

---

## ✅ Ready for Training!

Your dataset is now ready to use with:
- `train_emergency_model.py` (QLoRA script)
- `train_cpu_version.py` (CPU-friendly version)
- Any other Mistral-7B fine-tuning pipeline

**Recommended:** Start with `emergency_train.jsonl` (24 samples)
**Test with:** `emergency_test.jsonl` (6 samples)
