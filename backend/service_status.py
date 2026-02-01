def determine_service_status(data):
    distance_meters = data.get("distance_meters")
    
    if distance_meters is None or not isinstance(distance_meters, (int, float)) or distance_meters < 0:
        status = "assigned"
    elif distance_meters > 5000:
        status = "assigned"
    elif distance_meters > 500:
        status = "on_the_way"
    elif distance_meters > 50:
        status = "arriving"
    else:
        status = "arrived"
    
    return {
        "status": status
    }


if __name__ == "__main__":
    test_1 = {
        "distance_meters": 6000
    }
    print("Test 1 (6000m):", determine_service_status(test_1))
    
    test_2 = {
        "distance_meters": 3000
    }
    print("Test 2 (3000m):", determine_service_status(test_2))
    
    test_3 = {
        "distance_meters": 300
    }
    print("Test 3 (300m):", determine_service_status(test_3))
    
    test_4 = {
        "distance_meters": 20
    }
    print("Test 4 (20m):", determine_service_status(test_4))
    
    test_5 = {
        "distance_meters": -1
    }
    print("Test 5 (invalid -1):", determine_service_status(test_5))
