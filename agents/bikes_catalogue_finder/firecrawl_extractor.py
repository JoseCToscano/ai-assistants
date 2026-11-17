import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Try to import FirecrawlApp, with a helpful error if it's not installed
try:
    from firecrawl import FirecrawlApp
except ImportError:
    raise ImportError(
        "FirecrawlApp is required. Please install it with: pip install firecrawl"
    )

# Load environment variables
load_dotenv()

class BikePartExtractSchema(BaseModel):
    """Schema for bike part extraction"""
    product_name: str = Field(description="Full name of the product")
    brand: str = Field(description="Brand/manufacturer of the product")
    price: Optional[str] = Field(description="Price of the product if available")
    specifications: List[str] = Field(description="Key specifications of the product")
    compatibility: List[str] = Field(description="Vehicle compatibility information")
    availability: Optional[str] = Field(description="Availability status")
    url: str = Field(description="URL to the product page")

class FirecrawlExtractor:
    """Agent that uses Firecrawl to extract bike part information from websites"""
    
    def __init__(self):
        """Initialize the FirecrawlExtractor with API key from environment variables"""
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is not set")
        self.app = FirecrawlApp(api_key=api_key)
        
    def search_bike_parts(self, search_terms: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for bike parts using the provided search terms
        
        Args:
            search_terms: List of search terms to use
            max_results: Maximum number of results to return
            
        Returns:
            List of bike part information dictionaries
        """
        all_results = []
        
        for term in search_terms:
            # Create search URLs for common motorcycle parts retailers
            urls = [
                f"https://www.revzilla.com/search?term={term.replace(' ', '+')}",
                f"https://www.jpcycles.com/search?term={term.replace(' ', '+')}",
                f"https://www.denniskirk.com/search?q={term.replace(' ', '+')}",
                f"https://www.arlenness.com/search?q={term.replace(' ', '+')}",
            ]
            
            try:
                # Extract data using Firecrawl
                extraction_prompt = f"""
                Extract information about motorcycle parts matching this search: {term}
                
                Focus on finding products that match the search term. For each product, extract:
                - Full product name
                - Brand/manufacturer
                - Price (if available)
                - Key specifications
                - Vehicle compatibility information
                - Availability status
                - URL to the product page
                
                Only extract information for actual motorcycle parts, not accessories or other items.
                """
                
                data = self.app.extract(
                    urls,
                    {
                        "prompt": extraction_prompt,
                        "schema": BikePartExtractSchema.model_json_schema(),
                        "enableWebSearch": True
                    }
                )
                
                if data.get("success") and data.get("data"):
                    # Handle both list and single object responses
                    results = data.get("data")
                    if isinstance(results, list):
                        all_results.extend(results)
                    else:
                        all_results.append(results)
                
            except Exception as e:
                print(f"Error searching for term '{term}': {str(e)}")
        
        # Deduplicate results based on product_name and url
        unique_results = []
        seen_urls = set()
        
        for result in all_results:
            if result.get("url") and result.get("url") not in seen_urls:
                seen_urls.add(result.get("url"))
                unique_results.append(result)
                
                # Stop if we've reached max_results
                if len(unique_results) >= max_results:
                    break
        
        return unique_results
    
    def extract_from_specific_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Extract bike part information from specific URLs
        
        Args:
            urls: List of URLs to extract information from
            
        Returns:
            List of bike part information dictionaries
        """
        try:
            data = self.app.extract(
                urls,
                {
                    "prompt": """
                    Extract detailed information about the motorcycle part on this page.
                    Include the product name, brand, price, specifications, compatibility information,
                    availability status, and the URL to the product page.
                    """,
                    "schema": BikePartExtractSchema.model_json_schema()
                }
            )
            
            if data.get("success") and data.get("data"):
                # Handle both list and single object responses
                results = data.get("data")
                if isinstance(results, list):
                    return results
                else:
                    return [results]
            return []
            
        except Exception as e:
            print(f"Error extracting from URLs: {str(e)}")
            return []
    
    def save_results_to_file(self, results: List[Dict[str, Any]], filename: str = "catalogue.json"):
        """
        Save the extraction results to a JSON file
        
        Args:
            results: List of bike part information dictionaries
            filename: Name of the file to save to
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(directory, filename)
        
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Saved {len(results)} results to {filepath}")

# Example usage
if __name__ == "__main__":
    extractor = FirecrawlExtractor()
    
    # Example search terms
    search_terms = [
        "Arlen Ness Carbon Fiber Fat Wrapper Front Fender Harley Touring",
        "Carbon Fiber front fender Harley",
        "Fat Wrapper fender Harley"
    ]
    
    results = extractor.search_bike_parts(search_terms)
    extractor.save_results_to_file(results)
    
    print(f"Found {len(results)} bike parts")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('product_name', 'Unknown Product')}")
        print(f"   Brand: {result.get('brand', 'Unknown')}")
        print(f"   Price: {result.get('price', 'Not available')}")
        print(f"   URL: {result.get('url', 'No URL')}")
