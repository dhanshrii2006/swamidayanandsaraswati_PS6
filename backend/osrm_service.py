"""
OSRM (Open Source Routing Machine) service integration.
Calculates actual driving routes and ETA between locations.
"""

import requests
import sys
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Add current directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class OSRMService:
    """Service for calculating routes and ETAs using OSRM."""
    
    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        """
        Initialize OSRM service.
        
        Args:
            base_url: OSRM server URL (default uses public demo server)
        """
        self.base_url = base_url.rstrip('/')
    
    def calculate_route(self, origin: Dict[str, float], destination: Dict[str, float]) -> Optional[Dict]:
        """
        Calculate route between two points.
        
        Args:
            origin: Dict with 'lat' and 'lon' keys
            destination: Dict with 'lat' and 'lon' keys
        
        Returns:
            Dict with route information or None if request fails
        """
        try:
            # OSRM expects lon,lat format (not lat,lon!)
            url = f"{self.base_url}/route/v1/driving/{origin['lon']},{origin['lat']};{destination['lon']},{destination['lat']}"
            
            params = {
                'overview': 'false',
                'steps': 'false',
                'geometries': 'geojson'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                logger.error(f"OSRM error: {data.get('message')}")
                return None
            
            routes = data.get('routes', [])
            if not routes:
                logger.error("No routes found")
                return None
            
            route = routes[0]
            
            return {
                'distance_meters': route.get('distance', 0),
                'duration_seconds': route.get('duration', 0),
                'eta_minutes': round(route.get('duration', 0) / 60),
                'distance_km': round(route.get('distance', 0) / 1000, 2)
            }
            
        except requests.exceptions.Timeout:
            logger.error("OSRM request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"OSRM request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in OSRM service: {str(e)}")
            return None
    
    def calculate_matrix(self, origins: list, destinations: list) -> Optional[Dict]:
        """
        Calculate distance/duration matrix for multiple origins and destinations.
        Useful for finding nearest mechanic from multiple options.
        
        Args:
            origins: List of dicts with 'lat' and 'lon' keys
            destinations: List of dicts with 'lat' and 'lon' keys
        
        Returns:
            Dict with matrix data or None if request fails
        """
        try:
            # Build coordinates string (lon,lat format)
            coords = []
            for origin in origins:
                coords.append(f"{origin['lon']},{origin['lat']}")
            for dest in destinations:
                coords.append(f"{dest['lon']},{dest['lat']}")
            
            coords_string = ";".join(coords)
            
            # Sources are the first len(origins) coordinates
            sources = ";".join([str(i) for i in range(len(origins))])
            # Destinations are the remaining coordinates
            destinations_indices = ";".join([str(i) for i in range(len(origins), len(origins) + len(destinations))])
            
            url = f"{self.base_url}/table/v1/driving/{coords_string}"
            
            params = {
                'sources': sources,
                'destinations': destinations_indices
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 'Ok':
                logger.error(f"OSRM matrix error: {data.get('message')}")
                return None
            
            return {
                'durations': data.get('durations', []),
                'distances': data.get('distances', [])
            }
            
        except Exception as e:
            logger.error(f"OSRM matrix request failed: {str(e)}")
            return None


# Global instance
_osrm_service = None


def get_osrm_service(base_url: str = "http://router.project-osrm.org") -> OSRMService:
    """Get or create OSRM service instance."""
    global _osrm_service
    if _osrm_service is None:
        _osrm_service = OSRMService(base_url)
    return _osrm_service


def calculate_route_eta(origin: Dict[str, float], destination: Dict[str, float]) -> Dict:
    """
    Calculate ETA between two locations.
    
    Args:
        origin: Dict with 'lat' and 'lon' keys
        destination: Dict with 'lat' and 'lon' keys
    
    Returns:
        Dict with eta_minutes and distance_meters
    """
    service = get_osrm_service()
    result = service.calculate_route(origin, destination)
    
    if result:
        return {
            'eta_minutes': result['eta_minutes'],
            'distance_meters': result['distance_meters'],
            'distance_km': result['distance_km']
        }
    else:
        # Fallback to straight-line distance estimation
        try:
            from mechanic_selection import calculate_haversine_distance
        except ImportError:
            from backend.mechanic_selection import calculate_haversine_distance
        
        distance_meters = calculate_haversine_distance(
            origin['lat'], origin['lon'],
            destination['lat'], destination['lon']
        )
        
        # Rough estimation: assume 40 km/h average speed
        eta_minutes = int((distance_meters / 1000) / 40 * 60)
        
        logger.warning(f"Using fallback ETA calculation: {eta_minutes} minutes")
        
        return {
            'eta_minutes': eta_minutes,
            'distance_meters': distance_meters,
            'distance_km': round(distance_meters / 1000, 2)
        }


def find_nearest_with_eta(user_location: Dict[str, float], mechanics: list) -> Optional[Dict]:
    """
    Find nearest mechanic considering actual road distance/time.
    
    Args:
        user_location: Dict with 'lat' and 'lon' keys
        mechanics: List of mechanic dicts with 'id', 'lat', 'lon', 'available'
    
    Returns:
        Dict with mechanic_id, eta_minutes, distance_meters or None
    """
    if not mechanics:
        return None
    
    available_mechanics = [m for m in mechanics if m.get('available', False)]
    if not available_mechanics:
        return None
    
    service = get_osrm_service()
    
    # Prepare origins (mechanics) and destination (user)
    origins = [{'lat': m['lat'], 'lon': m['lon']} for m in available_mechanics]
    destinations = [user_location]
    
    matrix_result = service.calculate_matrix(origins, destinations)
    
    if matrix_result and matrix_result.get('durations'):
        durations = matrix_result['durations']
        distances = matrix_result.get('distances', [])
        
        # Find mechanic with minimum duration
        min_duration = float('inf')
        best_mechanic_idx = 0
        
        for idx, duration_row in enumerate(durations):
            if duration_row and duration_row[0] is not None:
                if duration_row[0] < min_duration:
                    min_duration = duration_row[0]
                    best_mechanic_idx = idx
        
        if min_duration != float('inf'):
            best_mechanic = available_mechanics[best_mechanic_idx]
            distance = distances[best_mechanic_idx][0] if distances else None
            
            return {
                'mechanic_id': best_mechanic['id'],
                'eta_minutes': round(min_duration / 60),
                'distance_meters': distance
            }
    
    # Fallback to haversine distance
    try:
        from mechanic_selection import select_nearest_mechanic
    except ImportError:
        from backend.mechanic_selection import select_nearest_mechanic
    
    result = select_nearest_mechanic({
        'user_location': user_location,
        'mechanics': available_mechanics
    })
    
    return result


if __name__ == "__main__":
    # Test OSRM service
    print("=" * 60)
    print("Testing OSRM Service")
    print("=" * 60)
    
    # Test 1: Calculate route between two points in Nagpur
    origin = {"lat": 21.1458, "lon": 79.0882}
    destination = {"lat": 21.1500, "lon": 79.0800}
    
    print("\nTest 1: Calculate route")
    print(f"Origin: {origin}")
    print(f"Destination: {destination}")
    
    result = calculate_route_eta(origin, destination)
    print(f"Result: {result}")
    
    # Test 2: Find nearest mechanic with actual ETA
    print("\n" + "=" * 60)
    print("Test 2: Find nearest mechanic with ETA")
    print("=" * 60)
    
    user_location = {"lat": 21.1458, "lon": 79.0882}
    mechanics = [
        {"id": "M01", "lat": 21.1500, "lon": 79.0800, "available": True},
        {"id": "M02", "lat": 21.1200, "lon": 79.1000, "available": True},
        {"id": "M03", "lat": 21.1600, "lon": 79.0900, "available": True}
    ]
    
    print(f"User location: {user_location}")
    print(f"Available mechanics: {len(mechanics)}")
    
    nearest = find_nearest_with_eta(user_location, mechanics)
    print(f"Nearest mechanic: {nearest}")
