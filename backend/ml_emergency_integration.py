"""
Integration Example: Using Strict JSON Prompts with Emergency Scoring
Shows how to replace rule-based logic with ML model
"""

from strict_json_prompts import get_recommended_prompt, extract_json_from_response
import json


# ============================================================================
# MOCK MODEL INFERENCE (Replace with actual model)
# ============================================================================

def mock_model_inference(prompt):
    """
    Mock function - Replace this with actual Mistral-7B inference.
    
    In production, use:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct")
        model = AutoModelForCausalLM.from_pretrained(...)
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.1)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    """
    # Mock responses for testing
    mock_responses = {
        "accident": '{"issue_type": "accident", "emergency_keywords": ["bleeding", "accident"]}',
        "fire": '{"issue_type": "fire", "emergency_keywords": ["fire", "flames"]}',
        "battery": '{"issue_type": "battery_dead", "emergency_keywords": []}',
        "flat": '{"issue_type": "flat_tire", "emergency_keywords": []}'
    }
    
    # Simple keyword matching for mock
    text_lower = prompt.lower()
    if "bleed" in text_lower or "injur" in text_lower:
        return mock_responses["accident"]
    elif "fire" in text_lower or "flame" in text_lower:
        return mock_responses["fire"]
    elif "battery" in text_lower:
        return mock_responses["battery"]
    else:
        return mock_responses["flat"]


# ============================================================================
# NEW ML-BASED EMERGENCY SCORING
# ============================================================================

def calculate_emergency_score_ml(data):
    """
    ML-based emergency scoring using Mistral-7B with strict JSON output.
    Drop-in replacement for the original calculate_emergency_score function.
    
    Args:
        data (dict): Input data with keys:
            - description: User's description text (REQUIRED for ML)
            - issue_type: (optional) Fallback if ML fails
            - emergency_keywords: (optional) Fallback if ML fails
    
    Returns:
        dict: Emergency score result with keys:
            - emergency_score: int (0-100)
            - emergency_flag: bool
            - issue_type: str
            - emergency_keywords: list
    """
    # Get user description
    description = data.get("description", "")
    
    if not description:
        # Fallback to rule-based if no description
        return calculate_emergency_score_fallback(data)
    
    try:
        # 1. Create strict JSON prompt
        prompt = get_recommended_prompt(description)
        
        # 2. Get model response
        model_response = mock_model_inference(prompt)
        
        # 3. Extract and validate JSON
        result = extract_json_from_response(model_response)
        
        if not result:
            # Fallback if extraction failed
            return calculate_emergency_score_fallback(data)
        
        # 4. Calculate emergency score
        score = 0
        issue_type = result.get("issue_type", "other")
        emergency_keywords = result.get("emergency_keywords", [])
        
        # Base score for issue type
        if issue_type == "accident":
            score += 60
        elif issue_type in ["fire", "gas_leak", "flood"]:
            score += 70
        elif issue_type in ["medical_emergency", "trapped"]:
            score += 80
        elif issue_type in ["brake_failure", "steering_failure"]:
            score += 65
        
        # Add points for emergency keywords
        score += len(emergency_keywords) * 15
        
        # Cap at 100
        score = min(score, 100)
        score = max(score, 0)
        
        # Determine emergency flag
        emergency_flag = score >= 70
        
        return {
            "emergency_score": score,
            "emergency_flag": emergency_flag,
            "issue_type": issue_type,
            "emergency_keywords": emergency_keywords
        }
        
    except Exception as e:
        print(f"ML scoring failed: {e}")
        return calculate_emergency_score_fallback(data)


def calculate_emergency_score_fallback(data):
    """
    Fallback to original rule-based scoring if ML fails.
    """
    score = 0
    
    issue_type = data.get("issue_type", "other")
    emergency_keywords = data.get("emergency_keywords", [])
    
    if issue_type == "accident":
        score += 60
    
    score += len(emergency_keywords) * 15
    score = min(score, 100)
    score = max(score, 0)
    
    emergency_flag = score >= 70
    
    return {
        "emergency_score": score,
        "emergency_flag": emergency_flag,
        "issue_type": issue_type,
        "emergency_keywords": emergency_keywords
    }


# ============================================================================
# HYBRID APPROACH (ML + Rules)
# ============================================================================

def calculate_emergency_score_hybrid(data):
    """
    Hybrid approach: Use ML for extraction, rules for scoring.
    Best of both worlds - flexible extraction with consistent scoring.
    """
    description = data.get("description", "")
    
    if description:
        # Use ML for extraction
        prompt = get_recommended_prompt(description)
        model_response = mock_model_inference(prompt)
        result = extract_json_from_response(model_response)
        
        if result:
            # Update data with ML results
            data["issue_type"] = result.get("issue_type", data.get("issue_type", "other"))
            data["emergency_keywords"] = result.get("emergency_keywords", data.get("emergency_keywords", []))
    
    # Use rule-based scoring
    return calculate_emergency_score_fallback(data)


# ============================================================================
# TESTING
# ============================================================================

def test_ml_scoring():
    """Test the ML-based scoring with various scenarios."""
    
    test_cases = [
        {
            "description": "Car accident near highway, person bleeding from head",
            "expected_emergency": True
        },
        {
            "description": "Vehicle caught fire, flames everywhere",
            "expected_emergency": True
        },
        {
            "description": "Battery is dead, won't start",
            "expected_emergency": False
        },
        {
            "description": "Flat tire on side of road",
            "expected_emergency": False
        },
    ]
    
    print("=" * 70)
    print("ML-BASED EMERGENCY SCORING TEST")
    print("=" * 70)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {test['description']}")
        
        result = calculate_emergency_score_ml({"description": test['description']})
        
        print(f"Issue Type: {result['issue_type']}")
        print(f"Emergency Keywords: {result['emergency_keywords']}")
        print(f"Score: {result['emergency_score']}")
        print(f"Emergency Flag: {result['emergency_flag']}")
        
        if result['emergency_flag'] == test['expected_emergency']:
            print("✓ Correct classification")
        else:
            print("✗ Incorrect classification")


# ============================================================================
# INTEGRATION GUIDE
# ============================================================================

def print_integration_guide():
    """Print instructions for integrating into the API."""
    
    print("\n" + "=" * 70)
    print("INTEGRATION GUIDE")
    print("=" * 70)
    
    print("""
1. Replace in api.py:
   
   OLD:
   from emergency_scoring import calculate_emergency_score
   
   NEW:
   from ml_emergency_integration import calculate_emergency_score_ml
   
2. Update workflow.py:
   
   emergency_result = calculate_emergency_score_ml({
       "description": request_data.get("description", ""),
       "issue_type": request_data.get("issue_type", ""),
       "emergency_keywords": request_data.get("emergency_keywords", [])
   })

3. Load model at API startup (api.py):
   
   from transformers import AutoTokenizer, AutoModelForCausalLM
   from peft import PeftModel
   
   # Load once at startup
   print("Loading ML model...")
   tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct")
   base_model = AutoModelForCausalLM.from_pretrained(
       "mistralai/Mistral-7B-Instruct",
       load_in_4bit=True,
       device_map="auto"
   )
   model = PeftModel.from_pretrained(base_model, "./emergency_lora_model")
   model.eval()

4. Replace mock_model_inference with real inference:
   
   def model_inference(prompt):
       inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
       with torch.no_grad():
           outputs = model.generate(
               **inputs,
               max_new_tokens=150,
               temperature=0.1,
               do_sample=True
           )
       return tokenizer.decode(outputs[0], skip_special_tokens=True)

5. Benefits:
   ✓ More accurate emergency detection
   ✓ Handles natural language descriptions
   ✓ Learns from data over time
   ✓ Consistent JSON output
   ✓ Fallback to rules if ML fails
""")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    test_ml_scoring()
    print_integration_guide()
    
    print("\n" + "=" * 70)
    print("✅ ML Integration Ready")
    print("=" * 70)
    print("\nUse calculate_emergency_score_ml() as drop-in replacement")
    print("Includes automatic fallback to rule-based scoring")
