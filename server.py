from flask import Flask
from flask_cors import CORS
from app import create_app
import logging

# Instead, use the standard logging module:
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/server.log')
    ]
)
logger = logging.getLogger(__name__)

# Create Flask application
app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    logger.info("Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5001)