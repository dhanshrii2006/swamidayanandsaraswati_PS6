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


def select_nearest_service_center(data):
    user_location = data.get("user_location")
    service_centers = data.get("service_centers", [])
    
    if not user_location or "lat" not in user_location or "lon" not in user_location:
        return {"selected_service_center_id": None}
    
    if not service_centers:
        return {"selected_service_center_id": None}
    
    user_lat = user_location["lat"]
    user_lon = user_location["lon"]
    
    min_distance = float("inf")
    nearest_center_id = None
    
    for center in service_centers:
        if "id" not in center or "lat" not in center or "lon" not in center:
            continue
        
        distance = calculate_haversine_distance(user_lat, user_lon, center["lat"], center["lon"])
        
        if distance < min_distance:
            min_distance = distance
            nearest_center_id = center["id"]
    
    return {"selected_service_center_id": nearest_center_id}


if __name__ == "__main__":
    test_1 = {
        "user_location": {"lat": 21.1458, "lon": 79.0882},
        "service_centers": [
            {"id": "SC01", "lat": 21.1500, "lon": 79.0800},
            {"id": "SC02", "lat": 21.1200, "lon": 79.1000}
        ]
    }
    print("Test 1 (two service centers):", select_nearest_service_center(test_1))
    
    test_2 = {
        "user_location": {"lat": 21.1458, "lon": 79.0882},
        "service_centers": []
    }
    print("Test 2 (empty service center list):", select_nearest_service_center(test_2))
