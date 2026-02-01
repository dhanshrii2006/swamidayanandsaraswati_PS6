# API Usage Guide

## 🚀 Starting the Server

### Option 1: Using Start Script (Recommended)
```powershell
# Windows PowerShell
.\start.ps1

# Or Command Prompt
start.bat
```

### Option 2: Manual Start
```powershell
# Initialize database (first time only)
E:/new/backend/venv/Scripts/python.exe init_db.py

# Start server
E:/new/backend/venv/Scripts/python.exe api.py
```

Server will be available at: **http://localhost:5000**

---

## 📍 Available Endpoints

### Root Endpoint
```bash
GET http://localhost:5000/
```
Returns API documentation and available endpoints.

### API Info
```bash
GET http://localhost:5000/api
```
Returns detailed endpoint information.

### Health Check
```bash
GET http://localhost:5000/api/health
```

---

## 🆕 Create Service Request

### Endpoint
```bash
POST http://localhost:5000/api/request
```

### Request Body
```json
{
  "user_id": "USER001",
  "issue_type": "flat_tire",
  "emergency_keywords": [],
  "description": "Flat tire on highway",
  "user_location": {
    "lat": 21.1458,
    "lon": 79.0882
  }
}
```

### Response (201 Created)
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "priority": "normal",
  "response_type": "mechanic",
  "emergency_flag": false,
  "selected_mechanic_id": "MECH001",
  "eta_minutes": 15,
  "service_status": "assigned"
}
```

### Emergency Request Example
```json
{
  "user_id": "USER002",
  "issue_type": "accident",
  "emergency_keywords": ["injured", "bleeding"],
  "description": "Car accident with injuries",
  "user_location": {
    "lat": 21.1500,
    "lon": 79.0800
  }
}
```

---

## 🔍 Get Request Details

### Endpoint
```bash
GET http://localhost:5000/api/request/<request_id>
```

### Example
```bash
GET http://localhost:5000/api/request/550e8400-e29b-41d4-a716-446655440000
```

### Response (200 OK)
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "USER001",
  "issue_type": "flat_tire",
  "description": "Flat tire on highway",
  "emergency_flag": false,
  "emergency_score": 0,
  "priority": "normal",
  "status": "assigned",
  "response_type": "mechanic",
  "selected_mechanic_id": "MECH001",
  "eta_minutes": 15,
  "mechanic_location": {
    "lat": 21.1500,
    "lon": 79.0800
  },
  "mechanic_name": "Suresh Mechanic",
  "mechanic_phone": "+919123456781",
  "created_at": "2026-02-01T10:30:00",
  "updated_at": "2026-02-01T10:30:05"
}
```

---

## 📍 Update Request Location

### Endpoint
```bash
POST http://localhost:5000/api/request/<request_id>/location
```

### Request Body
```json
{
  "lat": 21.1460,
  "lon": 79.0885
}
```

### Response (200 OK)
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "selected_mechanic_id": "MECH001",
  "eta_minutes": 12,
  "status": "assigned"
}
```

---

## ❌ Cancel Request

### Endpoint
```bash
PATCH http://localhost:5000/api/request/<request_id>/cancel
```

### Response (200 OK)
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "cancelled"
}
```

---

## 🚗 Update Mechanic Location

### Endpoint
```bash
POST http://localhost:5000/api/mechanic/<mechanic_id>/location
```

### Request Body
```json
{
  "lat": 21.1470,
  "lon": 79.0890
}
```

### Response (200 OK)
```json
{
  "mechanic_id": "MECH001",
  "location": {
    "lat": 21.1470,
    "lon": 79.0890
  },
  "status": "updated"
}
```

---

## 👥 List Mechanics

### Endpoint
```bash
GET http://localhost:5000/api/mechanics
```

### Response (200 OK)
```json
{
  "mechanics": [
    {
      "id": "MECH001",
      "name": "Suresh Mechanic",
      "phone": "+919123456781",
      "available": true,
      "location": {
        "lat": 21.1458,
        "lon": 79.0882
      },
      "current_request_id": null
    }
  ]
}
```

---

## 🏢 List Service Centers

### Endpoint
```bash
GET http://localhost:5000/api/service-centers
```

### Response (200 OK)
```json
{
  "service_centers": [
    {
      "id": "SC001",
      "name": "City Auto Care Center",
      "address": "123 Main Road, Nagpur",
      "phone": "+919123456790",
      "location": {
        "lat": 21.1450,
        "lon": 79.0850
      }
    }
  ]
}
```

---

## 🧪 Testing the API

### Run Automated Tests
```powershell
# Start the server first in one terminal
E:/new/backend/venv/Scripts/python.exe api.py

# Then run tests in another terminal
E:/new/backend/venv/Scripts/python.exe test_api.py
```

### Using curl
```bash
# Health check
curl http://localhost:5000/api/health

# Create request
curl -X POST http://localhost:5000/api/request \
  -H "Content-Type: application/json" \
  -d '{"user_id":"USER001","issue_type":"flat_tire","emergency_keywords":[],"user_location":{"lat":21.1458,"lon":79.0882}}'

# Get request
curl http://localhost:5000/api/request/<request_id>
```

### Using PowerShell
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get

# Create request
$body = @{
    user_id = "USER001"
    issue_type = "flat_tire"
    emergency_keywords = @()
    user_location = @{
        lat = 21.1458
        lon = 79.0882
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/request" -Method Post -Body $body -ContentType "application/json"
```

---

## ⚠️ Common Errors

### 404 - Endpoint Not Found
- Check you're using the correct URL path
- Use `/api/` prefix for all endpoints except root
- See available endpoints at: `http://localhost:5000/`

### 400 - Bad Request
- Check your JSON syntax
- Ensure all required fields are included
- Verify data types (lat/lon should be numbers)

### 404 - Request Not Found
- Verify the request_id exists
- Check if request was cancelled or deleted

### 500 - Internal Server Error
- Check server logs for details
- Ensure database is initialized
- Verify all dependencies are installed

---

## 🔧 Troubleshooting

### Server Won't Start
```powershell
# Check if database exists
dir roadside_assistance.db

# Initialize if missing
E:/new/backend/venv/Scripts/python.exe init_db.py

# Check for port conflicts
netstat -ano | findstr :5000
```

### Import Errors
```powershell
# Run integration tests
E:/new/backend/venv/Scripts/python.exe test_integration.py
```

### Database Issues
```powershell
# Delete and reinitialize
del roadside_assistance.db
E:/new/backend/venv/Scripts/python.exe init_db.py
```

---

## 📊 Sample Data

The `init_db.py` script creates:
- **3 Users**: USER001, USER002, USER003
- **5 Mechanics**: MECH001-MECH005 (around Nagpur area)
- **3 Service Centers**: SC001-SC003

You can use these IDs for testing!
