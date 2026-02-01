"""
LLM Output Parser - Safely parse JSON from LLM responses and integrate with emergency scoring
"""

import json
import re
from emergency_scoring import calculate_emergency_score


def parse_llm_output(raw_output):
    """
    Safely parse JSON from raw LLM output.
    
    Args:
        raw_output (str): Raw text from LLM (may contain JSON wrapped in markdown, explanations, etc.)
    
    Returns:
        dict: Parsed JSON object, or None if parsing fails
    """
    if not raw_output or not isinstance(raw_output, str):
        return None
    
    # Try 1: Direct JSON parsing
    try:
        return json.loads(raw_output.strip())
    except json.JSONDecodeError:
        pass
    
    # Try 2: Remove markdown code blocks
    cleaned = raw_output.strip()
    if "```json" in cleaned:
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*$', '', cleaned)
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            pass
    
    if "```" in cleaned:
        cleaned = re.sub(r'```\s*', '', cleaned)
        try:
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            pass
    
    # Try 3: Extract JSON with regex
    json_pattern = r'\{[^{}]*\}'
    matches = re.findall(json_pattern, raw_output)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Try 4: Find nested JSON
    json_pattern_nested = r'\{(?:[^{}]|\{[^{}]*\})*\}'
    matches = re.findall(json_pattern_nested, raw_output)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    return None


def process_llm_response(raw_output, default_issue_type="other"):
    """
    Process LLM output and calculate emergency score.
    
    Args:
        raw_output (str): Raw LLM response
        default_issue_type (str): Default issue type if parsing fails
    
    Returns:
        dict: Emergency score result with keys:
            - emergency_score: int
            - emergency_flag: bool
            - issue_type: str
            - emergency_keywords: list
            - parse_success: bool (indicates if JSON parsing succeeded)
    """
    # Parse JSON from LLM output
    parsed_data = parse_llm_output(raw_output)
    
    if parsed_data:
        # Extract fields from parsed JSON
        issue_type = parsed_data.get("issue_type", default_issue_type)
        emergency_keywords = parsed_data.get("emergency_keywords", [])
        parse_success = True
    else:
        # Fallback if parsing fails
        issue_type = default_issue_type
        emergency_keywords = []
        parse_success = False
    
    # Prepare data for emergency scoring
    score_data = {
        "issue_type": issue_type,
        "emergency_keywords": emergency_keywords
    }
    
    # Calculate emergency score
    result = calculate_emergency_score(score_data)
    
    # Add additional fields to result
    result["issue_type"] = issue_type
    result["emergency_keywords"] = emergency_keywords
    result["parse_success"] = parse_success
    
    return result


def batch_process_llm_responses(responses, default_issue_type="other"):
    """
    Process multiple LLM responses in batch.
    
    Args:
        responses (list): List of raw LLM output strings
        default_issue_type (str): Default issue type if parsing fails
    
    Returns:
        list: List of emergency score results
    """
    results = []
    for response in responses:
        result = process_llm_response(response, default_issue_type)
        results.append(result)
    return results


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("LLM OUTPUT PARSER TEST")
    print("=" * 70)
    
    # Test cases with various LLM output formats
    test_cases = [
        {
            "name": "Clean JSON",
            "output": '{"issue_type": "accident", "emergency_keywords": ["bleeding", "injured"]}'
        },
        {
            "name": "JSON with markdown",
            "output": '```json\n{"issue_type": "fire", "emergency_keywords": ["fire", "flames"]}\n```'
        },
        {
            "name": "JSON with explanation",
            "output": 'Based on the input, here is the extracted information:\n{"issue_type": "battery_dead", "emergency_keywords": []}\nThis is a non-emergency situation.'
        },
        {
            "name": "Messy format",
            "output": 'Sure! Here you go:\n\n```\n{"issue_type": "flat_tire", "emergency_keywords": []}\n```\n\nLet me know if you need anything else!'
        },
        {
            "name": "Invalid JSON",
            "output": 'This is not JSON at all, just plain text.'
        },
        {
            "name": "Partial JSON",
            "output": '{"issue_type": "engine_failure", "emergency_keywords": ["smoking"'
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Input: {test['output'][:60]}...")
        
        result = process_llm_response(test['output'])
        
        print(f"Parse Success: {result['parse_success']}")
        print(f"Issue Type: {result['issue_type']}")
        print(f"Emergency Keywords: {result['emergency_keywords']}")
        print(f"Emergency Score: {result['emergency_score']}")
        print(f"Emergency Flag: {result['emergency_flag']}")
    
    print("\n" + "=" * 70)
    print("✅ All tests completed")
    print("=" * 70)
