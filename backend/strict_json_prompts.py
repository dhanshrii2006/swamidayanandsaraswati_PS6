"""
Strict JSON Prompt Template for Mistral-7B-Instruct
Forces model to output valid JSON only, no explanations or markdown
"""

import json
import re


# ============================================================================
# STRICT JSON PROMPT TEMPLATES
# ============================================================================

STRICT_JSON_SYSTEM_PROMPT = """You are a JSON extraction API. You MUST respond with ONLY valid JSON, nothing else.

CRITICAL RULES:
1. Output ONLY the JSON object
2. NO explanations before or after
3. NO markdown code blocks (no ```json or ```)
4. NO extra text or commentary
5. MUST be valid, parseable JSON
6. Use ONLY the specified schema

Output schema:
{
  "issue_type": "string",
  "emergency_keywords": ["string", "string"]
}

Valid issue_types: accident, fire, engine, battery_dead, flat_tire, medical_emergency, gas_leak, flood, brake_failure, trapped, electrical, steering_failure, lockout, out_of_gas, maintenance, other"""


def create_strict_json_prompt(user_input):
    """
    Create Mistral instruction prompt that forces strict JSON output.
    
    Args:
        user_input: The user's text to extract from
        
    Returns:
        Formatted prompt string for Mistral-7B-Instruct
    """
    prompt = f"""<s>[INST] {STRICT_JSON_SYSTEM_PROMPT}

Extract emergency information from this text and respond with ONLY the JSON object:

Text: "{user_input}"

Remember: Output ONLY valid JSON, nothing else. [/INST] """
    
    return prompt


def create_strict_json_prompt_v2(user_input):
    """
    Alternative strict JSON prompt with more emphasis.
    
    Args:
        user_input: The user's text to extract from
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""<s>[INST] You are a JSON-only API. Extract emergency information and return ONLY valid JSON.

STRICT OUTPUT FORMAT (copy this structure exactly):
{{"issue_type": "string", "emergency_keywords": ["string"]}}

RULES:
- NO text before the JSON
- NO text after the JSON
- NO markdown (no ```json)
- NO explanations
- ONLY the JSON object

Text to analyze: "{user_input}"

Output (JSON only): [/INST] """
    
    return prompt


def create_strict_json_prompt_v3(user_input):
    """
    Ultra-strict prompt with JSON-mode instruction.
    
    Args:
        user_input: The user's text to extract from
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""<s>[INST] <JSON_MODE>

Task: Extract emergency data from text
Output: Valid JSON object ONLY

Schema:
{{
  "issue_type": "accident|fire|engine|battery_dead|flat_tire|medical_emergency|gas_leak|flood|brake_failure|trapped|electrical|steering_failure|lockout|out_of_gas|maintenance|other",
  "emergency_keywords": ["keyword1", "keyword2"]
}}

Input text: "{user_input}"

Output ONLY the JSON (no other text): [/INST] {{"issue_type": """
    
    return prompt


def create_strict_json_prompt_few_shot(user_input):
    """
    Few-shot prompt with examples showing JSON-only output.
    
    Args:
        user_input: The user's text to extract from
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""<s>[INST] Extract emergency information and return ONLY valid JSON. NO explanations.

Example 1:
Input: "Car accident with injuries"
Output: {{"issue_type": "accident", "emergency_keywords": ["accident", "injuries"]}}

Example 2:
Input: "Battery dead"
Output: {{"issue_type": "battery_dead", "emergency_keywords": []}}

Example 3:
Input: "Fire in engine, smoke everywhere"
Output: {{"issue_type": "fire", "emergency_keywords": ["fire", "smoke"]}}

Now extract from this text (JSON only):
"{user_input}" [/INST] """
    
    return prompt


# ============================================================================
# JSON VALIDATION AND CLEANING
# ============================================================================

def extract_json_from_response(response):
    """
    Extract and validate JSON from model response, handling common issues.
    
    Args:
        response: Raw model output
        
    Returns:
        Parsed JSON dict or None if invalid
    """
    # Remove special tokens
    response = response.replace('<s>', '').replace('</s>', '').strip()
    
    # Remove [INST] tags if present
    if '[/INST]' in response:
        response = response.split('[/INST]')[-1].strip()
    
    # Remove markdown code blocks
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*', '', response)
    
    # Remove any text before first {
    if '{' in response:
        response = response[response.find('{'):]
    
    # Remove any text after last }
    if '}' in response:
        response = response[:response.rfind('}')+1]
    
    # Try to parse
    try:
        data = json.loads(response)
        
        # Validate schema
        if not isinstance(data, dict):
            return None
            
        if 'issue_type' not in data or 'emergency_keywords' not in data:
            return None
            
        if not isinstance(data['emergency_keywords'], list):
            return None
        
        return data
        
    except json.JSONDecodeError:
        return None


def force_valid_json(response):
    """
    Aggressively clean and force valid JSON from response.
    
    Args:
        response: Raw model output
        
    Returns:
        Valid JSON string or default fallback
    """
    # Try standard extraction
    data = extract_json_from_response(response)
    if data:
        return json.dumps(data, ensure_ascii=False)
    
    # Fallback: construct from patterns
    issue_type = "other"
    emergency_keywords = []
    
    # Try to find issue_type
    issue_match = re.search(r'"issue_type"\s*:\s*"([^"]+)"', response)
    if issue_match:
        issue_type = issue_match.group(1)
    
    # Try to find keywords
    keywords_match = re.search(r'"emergency_keywords"\s*:\s*\[(.*?)\]', response, re.DOTALL)
    if keywords_match:
        keywords_str = keywords_match.group(1)
        keywords = re.findall(r'"([^"]+)"', keywords_str)
        emergency_keywords = keywords
    
    return json.dumps({
        "issue_type": issue_type,
        "emergency_keywords": emergency_keywords
    }, ensure_ascii=False)


# ============================================================================
# TESTING AND VALIDATION
# ============================================================================

def test_prompts():
    """Test all prompt templates."""
    test_input = "Car accident with person bleeding"
    
    print("=" * 70)
    print("STRICT JSON PROMPT TEMPLATES")
    print("=" * 70)
    
    print("\n1. VERSION 1 (Standard Strict):")
    print("-" * 70)
    print(create_strict_json_prompt(test_input))
    
    print("\n2. VERSION 2 (Format Emphasis):")
    print("-" * 70)
    print(create_strict_json_prompt_v2(test_input))
    
    print("\n3. VERSION 3 (JSON Mode):")
    print("-" * 70)
    print(create_strict_json_prompt_v3(test_input))
    
    print("\n4. VERSION 4 (Few-shot):")
    print("-" * 70)
    print(create_strict_json_prompt_few_shot(test_input))


def test_json_extraction():
    """Test JSON extraction from various response formats."""
    test_cases = [
        # Clean JSON
        '{"issue_type": "accident", "emergency_keywords": ["bleeding"]}',
        
        # With markdown
        '```json\n{"issue_type": "accident", "emergency_keywords": ["bleeding"]}\n```',
        
        # With explanation before
        'Here is the JSON: {"issue_type": "accident", "emergency_keywords": ["bleeding"]}',
        
        # With explanation after
        '{"issue_type": "accident", "emergency_keywords": ["bleeding"]} - This is an emergency',
        
        # With special tokens
        '<s>[INST]...[/INST] {"issue_type": "accident", "emergency_keywords": ["bleeding"]}</s>',
        
        # Messy format
        '  \n\n{"issue_type": "fire", "emergency_keywords": ["fire", "smoke"]}\n\nThis represents...',
    ]
    
    print("\n" + "=" * 70)
    print("JSON EXTRACTION TESTS")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Input: {test_case[:60]}...")
        result = extract_json_from_response(test_case)
        if result:
            print(f"✓ Extracted: {json.dumps(result)}")
        else:
            print(f"✗ Failed to extract")
            forced = force_valid_json(test_case)
            print(f"  Forced result: {forced}")


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def example_usage():
    """Show how to use the strict JSON prompts."""
    
    print("\n" + "=" * 70)
    print("USAGE EXAMPLE")
    print("=" * 70)
    
    user_text = "Serious car accident, driver bleeding from head injury"
    
    # Create prompt
    prompt = create_strict_json_prompt(user_text)
    
    print("\n1. Create Prompt:")
    print(prompt)
    
    print("\n2. Send to Model:")
    print("# Use with transformers:")
    print("# inputs = tokenizer(prompt, return_tensors='pt')")
    print("# outputs = model.generate(**inputs, max_new_tokens=100)")
    print("# response = tokenizer.decode(outputs[0])")
    
    print("\n3. Extract JSON:")
    mock_response = '{"issue_type": "accident", "emergency_keywords": ["bleeding", "accident", "head injury"]}'
    print(f"Mock response: {mock_response}")
    
    result = extract_json_from_response(mock_response)
    print(f"Extracted: {json.dumps(result, indent=2)}")


# ============================================================================
# RECOMMENDED PROMPT
# ============================================================================

def get_recommended_prompt(user_input):
    """
    Returns the recommended prompt template.
    This is the most effective version based on testing.
    
    Args:
        user_input: User's text to analyze
        
    Returns:
        Formatted prompt string
    """
    return create_strict_json_prompt_few_shot(user_input)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    test_prompts()
    test_json_extraction()
    example_usage()
    
    print("\n" + "=" * 70)
    print("✅ RECOMMENDED USAGE")
    print("=" * 70)
    print("\nUse: get_recommended_prompt(user_input)")
    print("Then: extract_json_from_response(model_output)")
