def resolve_location(data):
    response_type = data.get("response_type", "")
    
    if response_type == "request_location":
        action = "ask_landmark"
        user_message = "Please share a nearby landmark so we can send help."
    else:
        action = "proceed"
        user_message = None
    
    return {
        "action": action,
        "user_message": user_message
    }


if __name__ == "__main__":
    test_1 = {
        "response_type": "mechanic"
    }
    print("Test 1 (mechanic response):", resolve_location(test_1))
    
    test_2 = {
        "response_type": "request_location"
    }
    print("Test 2 (request location):", resolve_location(test_2))
