from flask import Blueprint, jsonify, request
import logging
from agents.calendar_agent import CalendarAgent

logger = logging.getLogger(__name__)
calendar_bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')
calendar_agent = CalendarAgent()

@calendar_bp.route('/list', methods=['GET'])
def list_calendars():
    """List all available calendars."""
    try:
        result = calendar_agent.list_calendars()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing calendars: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to list calendars: {str(e)}'
        }), 500

@calendar_bp.route('/events', methods=['GET'])
def list_events():
    """List events from a calendar."""
    try:
        calendar_id = request.args.get('calendar_id', 'primary')
        max_results = int(request.args.get('max_results', 10))
        
        result = calendar_agent.list_upcoming_events(
            calendar_id=calendar_id,
            max_results=max_results
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing events: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to list events: {str(e)}'
        }), 500 