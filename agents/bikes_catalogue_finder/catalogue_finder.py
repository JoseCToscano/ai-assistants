import os
import re
import json
import requests
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

# Load environment variables
load_dotenv()

class CatalogueFinder:
    """
    An AI agent that helps find bike parts in catalogues or online.
    It extracts key information from user requests and generates search queries.
    """
    
    def __init__(self):
        """Initialize the CatalogueFinder agent with the Claude API client."""
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Default search sources if none specified
        self.default_sources = [
            "online retailers",
            "manufacturer catalogues",
            "bike shop inventory systems"
        ]
    
    def process_request(self, user_request: str) -> Dict:
        """
        Process a user request to find bike parts.
        
        Args:
            user_request: The user's request text
            
        Returns:
            Dict containing extracted parts, search locations, and generated keywords
        """
        # Extract information using Claude
        extracted_info = self._extract_information(user_request)
        
        return {
            "parts": extracted_info["parts"],
            "specifications": extracted_info["specifications"],
            "search_locations": extracted_info["search_locations"],
            "search_keywords": extracted_info["search_keywords"],
            "vehicle": extracted_info["vehicle"]
        }
    
    def _extract_information(self, user_request: str) -> Dict:
        """
        Use Claude to extract parts, specifications, search locations, and vehicle information from the request.
        
        Args:
            user_request: The user's request text
            
        Returns:
            Dict with extracted parts, specifications, search locations, and vehicle information
        """
        prompt = f"""
        You are a bike shop assistant. Extract the following information from this customer request:
        
        1. What specific bike part(s) or component(s) is the customer looking for?
        2. What specifications or details did they mention about the part(s)?
        3. Did they mention where to search for the part(s)? If not, leave this blank.
        4. Did they mention a specific bike or motorcycle make and model? If so, extract both make and model.
        5. Come up with a list of search keywords based on the parts and specifications to be used for a search engine.
        
        Format your response as JSON with the keys: "parts" (list), "specifications" (list),"search_engine_query" (string), "search_locations" (list), and "vehicle" (object with "make" and "model" keys).
        
        Customer request: {user_request}
        """
        
        response = self.anthropic.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0,
            system="You extract structured information from bike part requests and return only valid JSON.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract the JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response.content[0].text, re.DOTALL)
        if json_match:
            extracted_json = json_match.group(1)
        else:
            # If no JSON code block, try to find JSON directly
            extracted_json = response.content[0].text
        
        try:
            result = json.loads(extracted_json)
            
            # If no search locations specified, use defaults
            if not result.get("search_locations") or len(result["search_locations"]) == 0:
                result["search_locations"] = self.default_sources
                
            # Ensure vehicle information exists
            if not result.get("vehicle"):
                result["vehicle"] = {"make": None, "model": None}
                
            return result
        except json.JSONDecodeError:
            # Fallback with empty values if JSON parsing fails
            return {
                "parts": [],
                "specifications": [],
                "search_locations": self.default_sources,
                "search_keywords": [],
                "vehicle": {"make": None, "model": None}
            }
    
    
    def generate_firecrawl_prompt(self, user_request: str) -> str:
        """
        Generate a structured prompt for an AI agent using FireCrawl to search for bike parts.
        
        Args:
            user_request: The user's request text
            
        Returns:
            A structured prompt for the FireCrawl AI agent
        """
        # Process the request
        processed_info = self.process_request(user_request)
        
        # Extract key information
        parts = processed_info["parts"]
        specifications = processed_info["specifications"]
        search_keywords = processed_info["search_keywords"]
        vehicle = processed_info["vehicle"]
        
        # Build the search prompt
        prompt = "# Bike Part Search Instructions\n\n"
        
        # Add the original request
        prompt += f"## Original Request\n{user_request}\n\n"
        
        # Add parts information
        prompt += "## Parts to Find\n"
        if parts:
            for part in parts:
                prompt += f"- {part}\n"
        else:
            prompt += "- No specific parts identified. Please search for general bike components based on the request.\n"
        
        # Add specifications
        prompt += "\n## Specifications\n"
        if specifications:
            for spec in specifications:
                prompt += f"- {spec}\n"
        else:
            prompt += "- No specific specifications mentioned.\n"
        
        # Add vehicle information if available
        if vehicle["make"] or vehicle["model"]:
            prompt += "\n## Vehicle Information\n"
            if vehicle["make"]:
                prompt += f"- Make: {vehicle['make']}\n"
            if vehicle["model"]:
                prompt += f"- Model: {vehicle['model']}\n"
            prompt += "\nPlease ensure compatibility with this specific vehicle.\n"
        
        # Add search keywords
        prompt += "\n## Recommended Search Keywords\n"
        if search_keywords:
            for keyword in search_keywords[:8]:  # Limit to top 8 keywords
                prompt += f"- {keyword}\n"
        else:
            prompt += "- Use general bike component terms based on the request.\n"
        
        # Add search instructions
        prompt += """
## Search Instructions

1. Use the provided keywords to search for the requested bike parts.
2. Focus on finding products that match ALL the specifications mentioned.
3. For each product found, collect the following information:
   - Product name and brand
   - Price (if available)
   - Key specifications
   - Compatibility information
   - Link to the product page
   - Availability status
4. Compare options from different retailers or manufacturers.
5. Prioritize results from reputable bike component retailers and manufacturers.
6. If searching for compatibility with a specific bike model, include that in your search.

## Response Format

Please organize your findings by part type, and for each product include:
- Product name and manufacturer
- Price and where to buy
- How well it matches the requested specifications
- Any compatibility notes with the mentioned vehicle (if applicable)
- A direct link to purchase or learn more
"""
        
        # Add catalogue reference if needed
        prompt += """
## Additional Resources

Consider checking the following sources if relevant to this search:
- Manufacturer websites for the most accurate specifications
- Bike-specific retailers for availability and pricing
- Forums or review sites for compatibility information with specific bike models
- Technical documentation for compatibility charts
"""
        
        return prompt


    def get_best_urls_to_scrape(self, search_query: str, num_results: int = 5) -> List[str]:
        """
        Get the best URLs to scrape for a given search query using Google Search API.
        
        Args:
            search_query: The search query to use
            num_results: Number of results to return (default: 5)
            
        Returns:
            List of URLs to scrape
        """
        # Get API keys from environment variables
        google_api_key = os.getenv("GOOGLE_API_KEY")
        google_cx = os.getenv("GOOGLE_CX")  # Custom Search Engine ID
        
        if not google_api_key or not google_cx:
            print("Warning: Google Search API credentials not found in environment variables")
            return []
        
        # Build the Google Custom Search API URL
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": google_api_key,
            "cx": google_cx,
            "q": search_query,
            "num": min(num_results, 10)  # Google API allows max 10 results per request
        }
        
        try:
            # Make the request to Google Custom Search API
            response = requests.get(base_url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            search_results = response.json()
            
            # Extract URLs from the search results
            urls = []
            if "items" in search_results:
                for item in search_results["items"]:
                    urls.append(item["link"])
            
            return urls
        
        except requests.exceptions.RequestException as e:
            print(f"Error making Google Search API request: {e}")
            return []
        except (KeyError, ValueError) as e:
            print(f"Error parsing Google Search API response: {e}")
            return []

       