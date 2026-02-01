def calculate_emergency_score(data):
    score = 0
    
    issue_type = data.get("issue_type", "")
    emergency_keywords = data.get("emergency_keywords", [])
    
    if issue_type == "accident":
        score += 60
    
    score += len(emergency_keywords) * 15
    
    score = min(score, 100)
    score = max(score, 0)
    
    emergency_flag = score >= 70
    
    return {
        "emergency_score": score,
        "emergency_flag": emergency_flag
    }


if __name__ == "__main__":
    test_1 = {
        "issue_type": "accident",
        "emergency_keywords": ["injured", "bleeding"]
    }
    print("Test 1 (accident with 2 keywords):", calculate_emergency_score(test_1))
    
    test_2 = {
        "issue_type": "engine",
        "emergency_keywords": []
    }
    print("Test 2 (non-accident, no keywords):", calculate_emergency_score(test_2))
