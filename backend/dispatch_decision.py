def make_dispatch_decision(data):
    emergency_flag = data.get("emergency_flag", False)
    suspicious = data.get("suspicious", False)
    location_available = data.get("location_available", False)
    
    if emergency_flag:
        priority = "emergency"
        response_type = "ambulance_police_and_mechanic"
    else:
        if suspicious:
            priority = "low"
        else:
            priority = "normal"
        
        response_type = "mechanic"
    
    if not location_available:
        response_type = "request_location"
    
    return {
        "priority": priority,
        "response_type": response_type
    }


if __name__ == "__main__":
    test_1 = {
        "emergency_flag": True,
        "suspicious": False,
        "location_available": True
    }
    print("Test 1 (emergency case):", make_dispatch_decision(test_1))
    
    test_2 = {
        "emergency_flag": False,
        "suspicious": True,
        "location_available": True
    }
    print("Test 2 (suspicious non-emergency):", make_dispatch_decision(test_2))
    
    test_3 = {
        "emergency_flag": False,
        "suspicious": False,
        "location_available": True
    }
    print("Test 3 (normal case):", make_dispatch_decision(test_3))
    
    test_4 = {
        "emergency_flag": False,
        "suspicious": False,
        "location_available": False
    }
    print("Test 4 (location missing):", make_dispatch_decision(test_4))
