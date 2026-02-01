"""
Main workflow orchestrator for roadside assistance requests.
Chains all modules together to process requests from start to finish.
"""

import sys
import os

# Add current directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from emergency_scoring import calculate_emergency_score
    from misuse_detection import detect_misuse
    from dispatch_decision import make_dispatch_decision
    from location_resolution import resolve_location
    from mechanic_selection import select_nearest_mechanic
    from service_center_selection import select_nearest_service_center
    from eta_finalization import finalize_eta
    from service_status import determine_service_status
except ImportError as e:
    # Fallback for package-style imports
    try:
        from backend.emergency_scoring import calculate_emergency_score
        from backend.misuse_detection import detect_misuse
        from backend.dispatch_decision import make_dispatch_decision
        from backend.location_resolution import resolve_location
        from backend.mechanic_selection import select_nearest_mechanic
        from backend.service_center_selection import select_nearest_service_center
        from backend.eta_finalization import finalize_eta
        from backend.service_status import determine_service_status
    except ImportError:
        print(f"Import error: {e}")
        print("Make sure you're running from the correct directory or the backend package is installed.")
        raise


class WorkflowEngine:
    """Orchestrates the complete request processing workflow."""
    
    def __init__(self):
        self.current_step = None
    
    def process_new_request(self, request_data):
        """
        Process a new service request through the complete workflow.
        
        Args:
            request_data (dict): Initial request data with keys:
                - issue_type: str
                - emergency_keywords: list
                - request_count_last_10_min: int
                - cancel_count_today: int
                - user_location: dict with lat/lon (optional)
                - mechanics: list (optional)
                - service_centers: list (optional)
        
        Returns:
            dict: Complete workflow result
        """
        result = {
            "request_id": request_data.get("request_id"),
            "workflow_status": "processing",
            "steps": {}
        }
        
        # Step 1: Calculate emergency score
        self.current_step = "emergency_scoring"
        emergency_result = calculate_emergency_score({
            "issue_type": request_data.get("issue_type", ""),
            "emergency_keywords": request_data.get("emergency_keywords", [])
        })
        result["steps"]["emergency_scoring"] = emergency_result
        result["emergency_flag"] = emergency_result["emergency_flag"]
        result["emergency_score"] = emergency_result["emergency_score"]
        
        # Step 2: Detect misuse
        self.current_step = "misuse_detection"
        misuse_result = detect_misuse({
            "request_count_last_10_min": request_data.get("request_count_last_10_min", 0),
            "cancel_count_today": request_data.get("cancel_count_today", 0),
            "emergency_flag": emergency_result["emergency_flag"]
        })
        result["steps"]["misuse_detection"] = misuse_result
        result["suspicious"] = misuse_result["suspicious"]
        result["action"] = misuse_result["action"]
        
        # Step 3: Make dispatch decision
        self.current_step = "dispatch_decision"
        location_available = bool(request_data.get("user_location"))
        dispatch_result = make_dispatch_decision({
            "emergency_flag": emergency_result["emergency_flag"],
            "suspicious": misuse_result["suspicious"],
            "location_available": location_available
        })
        result["steps"]["dispatch_decision"] = dispatch_result
        result["priority"] = dispatch_result["priority"]
        result["response_type"] = dispatch_result["response_type"]
        
        # Step 4: Resolve location if needed
        self.current_step = "location_resolution"
        location_result = resolve_location({
            "response_type": dispatch_result["response_type"]
        })
        result["steps"]["location_resolution"] = location_result
        
        if location_result["action"] == "ask_landmark":
            result["workflow_status"] = "awaiting_location"
            result["message"] = location_result["user_message"]
            return result
        
        # Step 5: Select mechanic (if location available)
        if location_available and dispatch_result["response_type"] != "request_location":
            self.current_step = "mechanic_selection"
            mechanic_result = select_nearest_mechanic({
                "user_location": request_data.get("user_location"),
                "mechanics": request_data.get("mechanics", [])
            })
            result["steps"]["mechanic_selection"] = mechanic_result
            result["selected_mechanic_id"] = mechanic_result["selected_mechanic_id"]
            
            # Step 6: Select service center
            self.current_step = "service_center_selection"
            center_result = select_nearest_service_center({
                "user_location": request_data.get("user_location"),
                "service_centers": request_data.get("service_centers", [])
            })
            result["steps"]["service_center_selection"] = center_result
            result["selected_service_center_id"] = center_result["selected_service_center_id"]
            
            # Step 7: Calculate ETA (placeholder - would call OSRM service)
            self.current_step = "eta_finalization"
            osrm_eta = request_data.get("osrm_eta_minutes")  # Would be calculated from OSRM service
            eta_result = finalize_eta({
                "osrm_eta_minutes": osrm_eta
            })
            result["steps"]["eta_finalization"] = eta_result
            result["final_eta_minutes"] = eta_result["final_eta_minutes"]
            
            # Step 8: Determine initial service status
            self.current_step = "service_status"
            status_result = determine_service_status({
                "distance_meters": request_data.get("distance_meters", 10000)
            })
            result["steps"]["service_status"] = status_result
            result["status"] = status_result["status"]
        
        result["workflow_status"] = "completed"
        self.current_step = None
        return result
    
    def update_location(self, request_data, new_location):
        """
        Update location for a request that was awaiting location.
        
        Args:
            request_data (dict): Original request data
            new_location (dict): New location with lat/lon
        
        Returns:
            dict: Updated workflow result
        """
        request_data["user_location"] = new_location
        request_data["location_available"] = True
        return self.process_new_request(request_data)
    
    def update_mechanic_location(self, request_id, mechanic_location, user_location):
        """
        Update service status based on mechanic's current location.
        
        Args:
            request_id (str): Request identifier
            mechanic_location (dict): Mechanic's current lat/lon
            user_location (dict): User's lat/lon
        
        Returns:
            dict: Updated status
        """
        from mechanic_selection import calculate_haversine_distance
        
        distance_meters = calculate_haversine_distance(
            mechanic_location["lat"],
            mechanic_location["lon"],
            user_location["lat"],
            user_location["lon"]
        )
        
        status_result = determine_service_status({
            "distance_meters": distance_meters
        })
        
        return {
            "request_id": request_id,
            "distance_meters": distance_meters,
            "status": status_result["status"]
        }


if __name__ == "__main__":
    # Test the workflow
    engine = WorkflowEngine()
    
    print("=" * 60)
    print("Test 1: Emergency request with location")
    print("=" * 60)
    test_request_1 = {
        "request_id": "REQ001",
        "issue_type": "accident",
        "emergency_keywords": ["injured", "bleeding"],
        "request_count_last_10_min": 1,
        "cancel_count_today": 0,
        "user_location": {"lat": 21.1458, "lon": 79.0882},
        "mechanics": [
            {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": True},
            {"id": "M02", "lat": 21.1200, "lon": 79.1000, "available": True}
        ],
        "service_centers": [
            {"id": "SC01", "lat": 21.1500, "lon": 79.0800}
        ],
        "osrm_eta_minutes": 15,
        "distance_meters": 8000
    }
    result_1 = engine.process_new_request(test_request_1)
    print(f"Status: {result_1['workflow_status']}")
    print(f"Emergency: {result_1['emergency_flag']} (score: {result_1['emergency_score']})")
    print(f"Priority: {result_1['priority']}")
    print(f"Response Type: {result_1['response_type']}")
    print(f"Mechanic: {result_1.get('selected_mechanic_id')}")
    print(f"ETA: {result_1.get('final_eta_minutes')} minutes")
    print(f"Status: {result_1.get('status')}")
    
    print("\n" + "=" * 60)
    print("Test 2: Suspicious user without location")
    print("=" * 60)
    test_request_2 = {
        "request_id": "REQ002",
        "issue_type": "flat_tire",
        "emergency_keywords": [],
        "request_count_last_10_min": 6,
        "cancel_count_today": 4,
        "user_location": None
    }
    result_2 = engine.process_new_request(test_request_2)
    print(f"Status: {result_2['workflow_status']}")
    print(f"Suspicious: {result_2['suspicious']}")
    print(f"Priority: {result_2['priority']}")
    print(f"Message: {result_2.get('message')}")
    
    print("\n" + "=" * 60)
    print("Test 3: Normal request with location")
    print("=" * 60)
    test_request_3 = {
        "request_id": "REQ003",
        "issue_type": "battery_dead",
        "emergency_keywords": [],
        "request_count_last_10_min": 1,
        "cancel_count_today": 0,
        "user_location": {"lat": 21.1458, "lon": 79.0882},
        "mechanics": [
            {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": True}
        ],
        "service_centers": [
            {"id": "SC01", "lat": 21.1500, "lon": 79.0800}
        ],
        "osrm_eta_minutes": 20,
        "distance_meters": 3000
    }
    result_3 = engine.process_new_request(test_request_3)
    print(f"Status: {result_3['workflow_status']}")
    print(f"Priority: {result_3['priority']}")
    print(f"Mechanic: {result_3.get('selected_mechanic_id')}")
    print(f"Service Status: {result_3.get('status')}")
    
    print("\n" + "=" * 60)
    print("Test 4: Update mechanic location")
    print("=" * 60)
    status_update = engine.update_mechanic_location(
        "REQ001",
        {"lat": 21.1460, "lon": 79.0885},
        {"lat": 21.1458, "lon": 79.0882}
    )
    print(f"Distance: {status_update['distance_meters']:.0f} meters")
    print(f"Status: {status_update['status']}")
