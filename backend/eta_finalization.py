def finalize_eta(data):
    osrm_eta_minutes = data.get("osrm_eta_minutes")
    
    if osrm_eta_minutes is not None and isinstance(osrm_eta_minutes, (int, float)) and osrm_eta_minutes >= 0:
        final_eta_minutes = int(osrm_eta_minutes)
    else:
        final_eta_minutes = None
    
    return {
        "final_eta_minutes": final_eta_minutes
    }


if __name__ == "__main__":
    test_1 = {
        "osrm_eta_minutes": 18
    }
    print("Test 1 (valid ETA):", finalize_eta(test_1))
    
    test_2 = {
        "osrm_eta_minutes": None
    }
    print("Test 2 (None ETA):", finalize_eta(test_2))
    
    test_3 = {
        "osrm_eta_minutes": -5
    }
    print("Test 3 (invalid ETA):", finalize_eta(test_3))
