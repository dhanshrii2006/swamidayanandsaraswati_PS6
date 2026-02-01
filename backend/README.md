# Roadside Assistance Backend

A comprehensive REST API for managing roadside assistance requests with emergency detection, mechanic dispatch, and real-time tracking.

## Features

- **Emergency Detection**: Automatic scoring and flagging of emergency situations
- **Misuse Prevention**: Detects and deprioritizes suspicious request patterns
- **Smart Dispatch**: Intelligent routing based on location, urgency, and availability
- **Real-time Tracking**: Live mechanic location updates and ETA calculations
- **Route Optimization**: Integration with OSRM for accurate ETAs
- **Complete Workflow**: End-to-end request processing from creation to completion

## Project Structure

```
backend/
├── api.py                      # Flask REST API endpoints
├── workflow.py                 # Main workflow orchestrator
├── models.py                   # Database models (SQLAlchemy)
├── config.py                   # Configuration management
├── init_db.py                  # Database initialization script
├── osrm_service.py            # OSRM integration for routing
├── emergency_scoring.py        # Emergency detection logic
├── misuse_detection.py         # Abuse prevention
├── dispatch_decision.py        # Dispatch priority logic
├── location_resolution.py      # Location handling
├── mechanic_selection.py       # Mechanic assignment
├── service_center_selection.py # Service center assignment
├── eta_finalization.py        # ETA calculation
├── service_status.py          # Status tracking
├── requirements.txt           # Python dependencies
└── .env.example              # Environment variables template
```

## Installation

### 1. Clone the repository

```bash
cd e:\new\backend
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
copy .env.example .env
# Edit .env with your configuration
```

### 5. Initialize database

```bash
python init_db.py
```

## Usage

### Start the API server

```bash
python api.py
```

The API will be available at `http://localhost:5000`

### Test workflow standalone

```bash
python workflow.py
```

### Test OSRM service

```bash
python osrm_service.py
```

## API Endpoints

### Root & Info
- `GET /` - API documentation and available endpoints
- `GET /api` - Detailed API information

### Health Check
- `GET /api/health` - Server health status

### Requests
- `POST /api/request` - Create new service request
- `GET /api/request/<id>` - Get request details
- `POST /api/request/<id>/location` - Update request location
- `PATCH /api/request/<id>/cancel` - Cancel request

### Mechanics
- `GET /api/mechanics` - Get all mechanics and availability
- `POST /api/mechanic/<id>/location` - Update mechanic location

### Service Centers
- `GET /api/service-centers` - Get all service centers

## API Examples

### Create Request

```bash
curl -X POST http://localhost:5000/api/request \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER001",
    "issue_type": "flat_tire",
    "emergency_keywords": [],
    "description": "Flat tire on highway",
    "user_location": {"lat": 21.1458, "lon": 79.0882}
  }'
```

### Get Request Status

```bash
curl http://localhost:5000/api/request/<request_id>
```

### Update Mechanic Location

```bash
curl -X POST http://localhost:5000/api/mechanic/MECH001/location \
  -H "Content-Type: application/json" \
  -d '{"lat": 21.1460, "lon": 79.0885}'
```

## Workflow Logic

1. **Emergency Scoring** - Calculates score based on issue type and keywords
2. **Misuse Detection** - Checks for suspicious patterns
3. **Dispatch Decision** - Determines priority and response type
4. **Location Resolution** - Handles missing location data
5. **Mechanic Selection** - Finds nearest available mechanic
6. **Service Center Selection** - Identifies nearest service center
7. **ETA Calculation** - Uses OSRM for accurate routing
8. **Status Tracking** - Monitors distance and updates status

## Database Schema

- **users** - User accounts and behavior tracking
- **mechanics** - Mechanic profiles and availability
- **service_centers** - Repair facility information
- **requests** - Service requests and their status
- **request_history** - Audit trail of changes

## Configuration

Key settings in `.env`:

```env
DATABASE_URL=sqlite:///roadside_assistance.db
OSRM_BASE_URL=http://router.project-osrm.org
EMERGENCY_SCORE_THRESHOLD=70
MAX_REQUESTS_PER_10_MIN=5
MAX_CANCELS_PER_DAY=3
```

## Development

### Run tests
```bash
pytest
```

### Code formatting
```bash
black .
```

### Linting
```bash
flake8
```

## Production Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Use production database (PostgreSQL recommended)
3. Deploy with Gunicorn or Waitress
4. Set up HTTPS with reverse proxy (nginx)
5. Configure proper CORS origins
6. Set strong SECRET_KEY

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app

# Using Waitress (Windows)
waitress-serve --port=5000 api:app
```

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] SMS/Push notifications (Twilio, Firebase)
- [ ] Payment integration (Stripe)
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Multi-language support
- [ ] Chat support between user and mechanic
- [ ] Rating and review system
- [ ] Route replay and history

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.
