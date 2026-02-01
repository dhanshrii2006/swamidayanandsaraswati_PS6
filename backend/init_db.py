"""
Database initialization and seed data script.
Run this to create tables and populate with sample data.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api import app, db
    from models import User, Mechanic, ServiceCenter, Request
except ImportError:
    from backend.api import app, db
    from backend.models import User, Mechanic, ServiceCenter, Request

import uuid
from datetime import datetime


def init_database():
    """Initialize database and create all tables."""
    with app.app_context():
        # Drop all tables (careful in production!)
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating tables...")
        db.create_all()
        
        print("Database initialized successfully!")


def seed_data():
    """Populate database with sample data for testing."""
    with app.app_context():
        print("Seeding database with sample data...")
        
        # Create sample users
        users = [
            User(id="USER001", name="Rajesh Kumar", phone="+919876543210", email="rajesh@example.com"),
            User(id="USER002", name="Priya Sharma", phone="+919876543211", email="priya@example.com"),
            User(id="USER003", name="Amit Patel", phone="+919876543212", email="amit@example.com"),
        ]
        
        for user in users:
            db.session.add(user)
        
        # Create sample mechanics (around Nagpur area)
        mechanics = [
            Mechanic(
                id="MECH001",
                name="Suresh Mechanic",
                phone="+919123456781",
                email="suresh@mechanics.com",
                latitude=21.1458,
                longitude=79.0882,
                available=True,
                specialization="all",
                rating=4.8
            ),
            Mechanic(
                id="MECH002",
                name="Vijay Auto Service",
                phone="+919123456782",
                email="vijay@mechanics.com",
                latitude=21.1500,
                longitude=79.0800,
                available=True,
                specialization="battery,towing",
                rating=4.6
            ),
            Mechanic(
                id="MECH003",
                name="Ramesh Repairs",
                phone="+919123456783",
                email="ramesh@mechanics.com",
                latitude=21.1200,
                longitude=79.1000,
                available=True,
                specialization="all",
                rating=4.9
            ),
            Mechanic(
                id="MECH004",
                name="Krishna Motors",
                phone="+919123456784",
                email="krishna@mechanics.com",
                latitude=21.1600,
                longitude=79.0900,
                available=False,
                specialization="engine,electrical",
                rating=4.7
            ),
            Mechanic(
                id="MECH005",
                name="Manoj Quick Fix",
                phone="+919123456785",
                email="manoj@mechanics.com",
                latitude=21.1350,
                longitude=79.0950,
                available=True,
                specialization="tyre,battery",
                rating=4.5
            ),
        ]
        
        for mechanic in mechanics:
            db.session.add(mechanic)
        
        # Create sample service centers
        service_centers = [
            ServiceCenter(
                id="SC001",
                name="City Auto Care Center",
                address="123 Main Road, Nagpur",
                phone="+919123456790",
                email="contact@cityautocare.com",
                latitude=21.1450,
                longitude=79.0850,
                capacity=15,
                current_load=5,
                services="engine_repair,body_work,painting,electrical",
                rating=4.7
            ),
            ServiceCenter(
                id="SC002",
                name="Highway Service Hub",
                address="456 Highway Road, Nagpur",
                phone="+919123456791",
                email="info@highwayservice.com",
                latitude=21.1250,
                longitude=79.1050,
                capacity=20,
                current_load=8,
                services="towing,battery,tyre_change,fuel",
                rating=4.6
            ),
            ServiceCenter(
                id="SC003",
                name="Express Auto Workshop",
                address="789 Express Lane, Nagpur",
                phone="+919123456792",
                email="support@expressauto.com",
                latitude=21.1550,
                longitude=79.0750,
                capacity=10,
                current_load=3,
                services="quick_fix,battery,tyre_change,oil_change",
                rating=4.8
            ),
        ]
        
        for center in service_centers:
            db.session.add(center)
        
        # Commit all seed data
        db.session.commit()
        
        print(f"Created {len(users)} users")
        print(f"Created {len(mechanics)} mechanics")
        print(f"Created {len(service_centers)} service centers")
        print("Database seeded successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    print("\n1. Initializing database...")
    init_database()
    
    print("\n2. Seeding sample data...")
    seed_data()
    
    print("\n" + "=" * 60)
    print("Database setup complete!")
    print("=" * 60)
    print("\nYou can now start the API server with:")
    print("  python api.py")
