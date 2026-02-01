"""
REST API for roadside assistance service.
Provides endpoints for creating, managing, and tracking service requests.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid

try:
    from workflow import WorkflowEngine
    from models import db, Request, Mechanic, ServiceCenter, User
    from config import Config
    from osrm_service import calculate_route_eta
except ImportError:
    # Fallback for package-style imports
    from backend.workflow import WorkflowEngine
    from backend.models import db, Request, Mechanic, ServiceCenter, User
    from backend.config import Config
    from backend.osrm_service import calculate_route_eta

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize database
db.init_app(app)

# Initialize workflow engine
workflow_engine = WorkflowEngine()

# In-memory storage for demo (replace with database in production)
active_requests = {}


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API documentation."""
    return jsonify({
        "name": "Roadside Assistance API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "GET /api/health",
            "create_request": "POST /api/request",
            "get_request": "GET /api/request/<request_id>",
            "update_location": "POST /api/request/<request_id>/location",
            "cancel_request": "PATCH /api/request/<request_id>/cancel",
            "update_mechanic_location": "POST /api/mechanic/<mechanic_id>/location",
            "list_mechanics": "GET /api/mechanics",
            "list_service_centers": "GET /api/service-centers"
        },
        "documentation": "See README.md for detailed API documentation"
    }), 200


@app.route('/api', methods=['GET'])
def api_info():
    """API info endpoint."""
    return jsonify({
        "message": "Roadside Assistance API",
        "version": "1.0.0",
        "endpoints": [
            {"method": "GET", "path": "/api/health", "description": "Health check"},
            {"method": "POST", "path": "/api/request", "description": "Create new service request"},
            {"method": "GET", "path": "/api/request/<id>", "description": "Get request details"},
            {"method": "POST", "path": "/api/request/<id>/location", "description": "Update request location"},
            {"method": "PATCH", "path": "/api/request/<id>/cancel", "description": "Cancel request"},
            {"method": "POST", "path": "/api/mechanic/<id>/location", "description": "Update mechanic location"},
            {"method": "GET", "path": "/api/mechanics", "description": "List all mechanics"},
            {"method": "GET", "path": "/api/service-centers", "description": "List all service centers"}
        ]
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


@app.route('/api/request', methods=['POST'])
def create_request():
    """
    Create a new service request.
    
    Expected JSON body:
    {
        "user_id": "string",
        "issue_type": "accident|flat_tire|battery_dead|engine|other",
        "emergency_keywords": ["injured", "bleeding"],
        "description": "string",
        "user_location": {"lat": float, "lon": float} (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get("user_id"):
            return jsonify({"error": "user_id is required"}), 400
        
        if not data.get("issue_type"):
            return jsonify({"error": "issue_type is required"}), 400
        
        # Get user stats for misuse detection
        user = User.query.filter_by(id=data["user_id"]).first()
        if not user:
            # Create new user if doesn't exist
            user = User(id=data["user_id"])
            db.session.add(user)
            db.session.commit()
        
        request_count_last_10_min = user.get_recent_request_count()
        cancel_count_today = user.get_cancel_count_today()
        
        # Get available mechanics near location (if provided)
        mechanics = []
        service_centers = []
        osrm_eta = None
        distance_meters = None
        
        if data.get("user_location"):
            mechanics_query = Mechanic.query.filter_by(available=True).all()
            mechanics = [
                {
                    "id": m.id,
                    "lat": m.latitude,
                    "lon": m.longitude,
                    "available": m.available
                }
                for m in mechanics_query
            ]
            
            centers_query = ServiceCenter.query.all()
            service_centers = [
                {
                    "id": c.id,
                    "lat": c.latitude,
                    "lon": c.longitude
                }
                for c in centers_query
            ]
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Prepare workflow input
        workflow_input = {
            "request_id": request_id,
            "issue_type": data.get("issue_type"),
            "emergency_keywords": data.get("emergency_keywords", []),
            "request_count_last_10_min": request_count_last_10_min,
            "cancel_count_today": cancel_count_today,
            "user_location": data.get("user_location"),
            "mechanics": mechanics,
            "service_centers": service_centers,
            "osrm_eta_minutes": osrm_eta,
            "distance_meters": distance_meters
        }
        
        # Process through workflow
        result = workflow_engine.process_new_request(workflow_input)
        
        # If location available and mechanic selected, calculate actual ETA
        if result.get("selected_mechanic_id") and data.get("user_location"):
            mechanic = Mechanic.query.get(result["selected_mechanic_id"])
            if mechanic:
                eta_data = calculate_route_eta(
                    {"lat": mechanic.latitude, "lon": mechanic.longitude},
                    data["user_location"]
                )
                result["final_eta_minutes"] = eta_data.get("eta_minutes")
                distance_meters = eta_data.get("distance_meters")
        
        # Save to database
        new_request = Request(
            id=request_id,
            user_id=data["user_id"],
            issue_type=data.get("issue_type"),
            description=data.get("description", ""),
            emergency_score=result.get("emergency_score", 0),
            emergency_flag=result.get("emergency_flag", False),
            suspicious=result.get("suspicious", False),
            priority=result.get("priority", "normal"),
            response_type=result.get("response_type", "mechanic"),
            status=result.get("status", "assigned"),
            selected_mechanic_id=result.get("selected_mechanic_id"),
            selected_service_center_id=result.get("selected_service_center_id"),
            user_latitude=data.get("user_location", {}).get("lat"),
            user_longitude=data.get("user_location", {}).get("lon"),
            eta_minutes=result.get("final_eta_minutes")
        )
        db.session.add(new_request)
        
        # Update mechanic availability if assigned
        if result.get("selected_mechanic_id"):
            mechanic = Mechanic.query.get(result["selected_mechanic_id"])
            if mechanic:
                mechanic.available = False
                mechanic.current_request_id = request_id
        
        db.session.commit()
        
        # Store in memory for quick access
        active_requests[request_id] = result
        
        return jsonify({
            "request_id": request_id,
            "status": result.get("workflow_status"),
            "priority": result.get("priority"),
            "response_type": result.get("response_type"),
            "emergency_flag": result.get("emergency_flag"),
            "message": result.get("message"),
            "selected_mechanic_id": result.get("selected_mechanic_id"),
            "eta_minutes": result.get("final_eta_minutes"),
            "service_status": result.get("status")
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/request/<request_id>', methods=['GET'])
def get_request(request_id):
    """Get details of a specific request."""
    try:
        req = Request.query.get(request_id)
        if not req:
            return jsonify({"error": "Request not found"}), 404
        
        response = {
            "request_id": req.id,
            "user_id": req.user_id,
            "issue_type": req.issue_type,
            "description": req.description,
            "emergency_flag": req.emergency_flag,
            "emergency_score": req.emergency_score,
            "priority": req.priority,
            "status": req.status,
            "response_type": req.response_type,
            "selected_mechanic_id": req.selected_mechanic_id,
            "selected_service_center_id": req.selected_service_center_id,
            "eta_minutes": req.eta_minutes,
            "created_at": req.created_at.isoformat(),
            "updated_at": req.updated_at.isoformat()
        }
        
        # Add mechanic location if assigned
        if req.selected_mechanic_id:
            mechanic = Mechanic.query.get(req.selected_mechanic_id)
            if mechanic:
                response["mechanic_location"] = {
                    "lat": mechanic.latitude,
                    "lon": mechanic.longitude
                }
                response["mechanic_name"] = mechanic.name
                response["mechanic_phone"] = mechanic.phone
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/request/<request_id>/location', methods=['POST'])
def update_request_location(request_id):
    """
    Update location for a request that was awaiting location.
    
    Expected JSON body:
    {
        "lat": float,
        "lon": float
    }
    """
    try:
        req = Request.query.get(request_id)
        if not req:
            return jsonify({"error": "Request not found"}), 404
        
        data = request.get_json()
        if not data.get("lat") or not data.get("lon"):
            return jsonify({"error": "lat and lon are required"}), 400
        
        # Update location
        req.user_latitude = data["lat"]
        req.user_longitude = data["lon"]
        
        # Re-process workflow with new location
        user = User.query.get(req.user_id)
        
        mechanics_query = Mechanic.query.filter_by(available=True).all()
        mechanics = [
            {
                "id": m.id,
                "lat": m.latitude,
                "lon": m.longitude,
                "available": m.available
            }
            for m in mechanics_query
        ]
        
        centers_query = ServiceCenter.query.all()
        service_centers = [
            {
                "id": c.id,
                "lat": c.latitude,
                "lon": c.longitude
            }
            for c in centers_query
        ]
        
        workflow_input = {
            "request_id": request_id,
            "issue_type": req.issue_type,
            "emergency_keywords": [],  # Already processed
            "request_count_last_10_min": 0,
            "cancel_count_today": 0,
            "user_location": {"lat": data["lat"], "lon": data["lon"]},
            "mechanics": mechanics,
            "service_centers": service_centers
        }
        
        result = workflow_engine.process_new_request(workflow_input)
        
        # Update request with new data
        req.selected_mechanic_id = result.get("selected_mechanic_id")
        req.selected_service_center_id = result.get("selected_service_center_id")
        req.status = result.get("status", "assigned")
        
        # Calculate actual ETA
        if result.get("selected_mechanic_id"):
            mechanic = Mechanic.query.get(result["selected_mechanic_id"])
            if mechanic:
                eta_data = calculate_route_eta(
                    {"lat": mechanic.latitude, "lon": mechanic.longitude},
                    {"lat": data["lat"], "lon": data["lon"]}
                )
                req.eta_minutes = eta_data.get("eta_minutes")
                mechanic.available = False
                mechanic.current_request_id = request_id
        
        db.session.commit()
        
        return jsonify({
            "request_id": request_id,
            "selected_mechanic_id": req.selected_mechanic_id,
            "eta_minutes": req.eta_minutes,
            "status": req.status
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/request/<request_id>/cancel', methods=['PATCH'])
def cancel_request(request_id):
    """Cancel a service request."""
    try:
        req = Request.query.get(request_id)
        if not req:
            return jsonify({"error": "Request not found"}), 404
        
        # Update request status
        req.status = "cancelled"
        req.cancelled_at = datetime.utcnow()
        
        # Free up mechanic if assigned
        if req.selected_mechanic_id:
            mechanic = Mechanic.query.get(req.selected_mechanic_id)
            if mechanic:
                mechanic.available = True
                mechanic.current_request_id = None
        
        # Update user cancel count
        user = User.query.get(req.user_id)
        if user:
            user.increment_cancel_count()
        
        db.session.commit()
        
        return jsonify({
            "request_id": request_id,
            "status": "cancelled"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/mechanic/<mechanic_id>/location', methods=['POST'])
def update_mechanic_location(mechanic_id):
    """
    Update mechanic's current location (for tracking).
    
    Expected JSON body:
    {
        "lat": float,
        "lon": float
    }
    """
    try:
        mechanic = Mechanic.query.get(mechanic_id)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404
        
        data = request.get_json()
        if not data.get("lat") or not data.get("lon"):
            return jsonify({"error": "lat and lon are required"}), 400
        
        # Update mechanic location
        mechanic.latitude = data["lat"]
        mechanic.longitude = data["lon"]
        
        # Update status of current request if any
        if mechanic.current_request_id:
            req = Request.query.get(mechanic.current_request_id)
            if req and req.user_latitude and req.user_longitude:
                status_update = workflow_engine.update_mechanic_location(
                    req.id,
                    {"lat": data["lat"], "lon": data["lon"]},
                    {"lat": req.user_latitude, "lon": req.user_longitude}
                )
                req.status = status_update["status"]
        
        db.session.commit()
        
        return jsonify({
            "mechanic_id": mechanic_id,
            "location": {"lat": mechanic.latitude, "lon": mechanic.longitude},
            "status": "updated"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/mechanics', methods=['GET'])
def get_mechanics():
    """Get all mechanics and their availability."""
    try:
        mechanics = Mechanic.query.all()
        return jsonify({
            "mechanics": [
                {
                    "id": m.id,
                    "name": m.name,
                    "phone": m.phone,
                    "available": m.available,
                    "location": {"lat": m.latitude, "lon": m.longitude},
                    "current_request_id": m.current_request_id
                }
                for m in mechanics
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/service-centers', methods=['GET'])
def get_service_centers():
    """Get all service centers."""
    try:
        centers = ServiceCenter.query.all()
        return jsonify({
            "service_centers": [
                {
                    "id": c.id,
                    "name": c.name,
                    "address": c.address,
                    "phone": c.phone,
                    "location": {"lat": c.latitude, "lon": c.longitude}
                }
                for c in centers
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )
