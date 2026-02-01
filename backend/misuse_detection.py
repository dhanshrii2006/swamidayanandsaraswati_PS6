def detect_misuse(data):
    request_count_last_10_min = data.get("request_count_last_10_min", 0)
    cancel_count_today = data.get("cancel_count_today", 0)
    emergency_flag = data.get("emergency_flag", False)
    
    if emergency_flag:
        suspicious = False
        action = "normal"
    else:
        if request_count_last_10_min >= 5 or cancel_count_today >= 3:
            suspicious = True
            action = "deprioritize"
        else:
            suspicious = False
            action = "normal"
    
    return {
        "suspicious": suspicious,
        "action": action
    }


if __name__ == "__main__":
    test_1 = {
        "request_count_last_10_min": 2,
        "cancel_count_today": 1,
        "emergency_flag": False
    }
    print("Test 1 (normal user):", detect_misuse(test_1))
    
    test_2 = {
        "request_count_last_10_min": 6,
        "cancel_count_today": 2,
        "emergency_flag": False
    }
    print("Test 2 (suspicious user):", detect_misuse(test_2))
    
    test_3 = {
        "request_count_last_10_min": 10,
        "cancel_count_today": 5,
        "emergency_flag": True
    }
    print("Test 3 (emergency case):", detect_misuse(test_3))
