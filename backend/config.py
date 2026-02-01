"""
Configuration settings for roadside assistance backend.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Database settings
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')  # 'sqlite', 'postgresql', 'mysql'
    
    # SQLite configuration (default for development)
    if DATABASE_TYPE == 'sqlite':
        SQLALCHEMY_DATABASE_URI = os.getenv(
            'DATABASE_URL',
            'sqlite:///roadside_assistance.db'
        )
    # PostgreSQL configuration
    elif DATABASE_TYPE == 'postgresql':
        SQLALCHEMY_DATABASE_URI = os.getenv(
            'DATABASE_URL',
            'postgresql://user:password@localhost:5432/roadside_assistance'
        )
    # MySQL configuration
    elif DATABASE_TYPE == 'mysql':
        SQLALCHEMY_DATABASE_URI = os.getenv(
            'DATABASE_URL',
            'mysql://user:password@localhost:3306/roadside_assistance'
        )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    
    # OSRM settings
    OSRM_BASE_URL = os.getenv('OSRM_BASE_URL', 'http://router.project-osrm.org')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # API settings
    API_RATE_LIMIT = os.getenv('API_RATE_LIMIT', '100 per hour')
    
    # Emergency settings
    EMERGENCY_SCORE_THRESHOLD = int(os.getenv('EMERGENCY_SCORE_THRESHOLD', 70))
    
    # Misuse detection thresholds
    MAX_REQUESTS_PER_10_MIN = int(os.getenv('MAX_REQUESTS_PER_10_MIN', 5))
    MAX_CANCELS_PER_DAY = int(os.getenv('MAX_CANCELS_PER_DAY', 3))
    
    # Service status distance thresholds (in meters)
    DISTANCE_ASSIGNED = int(os.getenv('DISTANCE_ASSIGNED', 5000))
    DISTANCE_ON_THE_WAY = int(os.getenv('DISTANCE_ON_THE_WAY', 500))
    DISTANCE_ARRIVING = int(os.getenv('DISTANCE_ARRIVING', 50))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # External services (future integrations)
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    
    # Google Maps (for geocoding)
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    # Payment gateway (future)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Override with production database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/roadside_assistance'
    )


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
