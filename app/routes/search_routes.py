from flask import Blueprint, request, jsonify
import logging
from agents.bikes_catalogue_finder.catalogue_finder import CatalogueFinder
logger = logging.getLogger(__name__)
search_bp = Blueprint('search', __name__, url_prefix='/api')


@search_bp.route('/rag', methods=['POST'])
def rag():
    """Search for similar content using vector similarity"""
    query = request.json.get('query')
    conversation_id = request.json.get('conversation_id')
    
    
    if not query:
        return jsonify({'status': 'error', 'message': 'No query provided'}), 400
    
    catalogue_finder = CatalogueFinder()
    firecrawl_prompt = catalogue_finder.generate_firecrawl_prompt(query)
    urls = catalogue_finder.get_best_urls_to_scrape(firecrawl_prompt)
    
    return jsonify({
        'status': 'success',
        'query': query,
        'results': results
    })
