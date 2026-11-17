from flask import Flask
import logging

logger = logging.getLogger(__name__)

def create_app(config=None):
    """Initialize and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.from_object(config)
    
    # Register blueprints
    from app.routes.search_routes import search_bp
    from app.routes.calendar_routes import calendar_bp
    
    app.register_blueprint(search_bp)
    app.register_blueprint(calendar_bp)
    
    # Initialize services
    if initialize_services():
        logger.info("All services initialized successfully")
    else:
        logger.error("Failed to initialize one or more services")
    
    return app

def initialize_services():
    """Initialize all required services"""
    success = True
    
    return success
