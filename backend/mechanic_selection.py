import math

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def select_nearest_mechanic(data):
    user_location = data.get("user_location")
    mechanics = data.get("mechanics", [])
    
    if not user_location or "lat" not in user_location or "lon" not in user_location:
        return {"selected_mechanic_id": None}
    
    if not mechanics:
        return {"selected_mechanic_id": None}
    
    user_lat = user_location["lat"]
    user_lon = user_location["lon"]
    
    min_distance = float("inf")
    nearest_mechanic_id = None
    
    for mechanic in mechanics:
        if not mechanic.get("available", False):
            continue
        
        if "id" not in mechanic or "lat" not in mechanic or "lon" not in mechanic:
            continue
        
        distance = calculate_haversine_distance(user_lat, user_lon, mechanic["lat"], mechanic["lon"])
        
        if distance < min_distance:
            min_distance = distance
            nearest_mechanic_id = mechanic["id"]
    
    return {"selected_mechanic_id": nearest_mechanic_id}


if __name__ == "__main__":
    test_1 = {
        "user_location": {"lat": 21.1458, "lon": 79.0882},
        "mechanics": [
            {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": True},
            {"id": "M02", "lat": 21.1200, "lon": 79.1000, "available": True}
        ]
    }
    print("Test 1 (two available mechanics):", select_nearest_mechanic(test_1))
    
    test_2 = {
        "user_location": {"lat": 21.1458, "lon": 79.0882},
        "mechanics": [
            {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": True},
            {"id": "M02", "lat": 21.1200, "lon": 79.1000, "available": False}
        ]
    }
    print("Test 2 (one available, one unavailable):", select_nearest_mechanic(test_2))
    
    test_3 = {
        "user_location": {"lat": 21.1458, "lon": 79.0882},
        "mechanics": [
            {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": False},
            {"id": "M02", "lat": 21.1200, "lon": 79.1000, "available": False}
        ]
    }
    print("Test 3 (no available mechanics):", select_nearest_mechanic(test_3))
