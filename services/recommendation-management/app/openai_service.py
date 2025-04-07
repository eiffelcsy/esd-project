import os
from openai import OpenAI
import json
from datetime import date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_env_var(key, default=None):
    value = os.environ.get(key, default)
    if value is None or value.strip() == '':
        logger.error(f"Missing required environment variable: {key}")
        return None
    return value.strip()

def get_openai_client():
    """Initialize and return an OpenAI client, or None if initialization fails"""
    try:
        api_key = get_env_var('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY is empty or not set")
            return None
        
        client = OpenAI(api_key=api_key)
        logger.info("Successfully initialized OpenAI client")
        return client
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {e}")
        logger.error("Please ensure OPENAI_API_KEY is properly set in your environment")
        return None

def get_recommendations(destination, start_date, end_date):
    logger.info(f"Getting recommendations for {destination} from {start_date} to {end_date}")
    
    # Initialize the OpenAI client within this function
    client = get_openai_client()
    if not client:
        logger.error("Failed to initialize OpenAI client, returning fallback recommendations")
        return get_fallback_recommendations(destination)

    # Calculate trip duration
    trip_duration = (end_date - start_date).days + 1
    
    try:
        # Call OpenAI API
        logger.info("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant that provides detailed recommendations in JSON format."},
                {"role": "user", "content": create_prompt(destination, start_date, end_date, trip_duration)}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # Extract and parse the response
        result = response.choices[0].message.content
        logger.info("Received response from OpenAI API")
        
        # Clean up the response to ensure it's valid JSON
        result = result.replace("```json", "").replace("```", "").strip()
        
        try:
            recommendations = json.loads(result)
            logger.info("Successfully parsed OpenAI response")
            return recommendations
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {e}")
            return get_fallback_recommendations(destination)
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return get_fallback_recommendations(destination)

def create_prompt(destination, start_date, end_date, trip_duration):
    return f"""
    Create a detailed travel recommendation for a trip to {destination} from {start_date} to {end_date} ({trip_duration} days).
    
    Please provide:
    1. Top 5 must-see attractions
    2. 3 recommended restaurants or food experiences
    3. 2 off-the-beaten-path activities
    4. Any special events happening during these dates if known
    5. Practical tips specific to this destination and time period
    
    Format the response as a JSON object with the following structure:
    {{
        "attractions": [
            {{"name": "attraction name", "description": "brief description", "suggested_day": "day number or range"}}
        ],
        "restaurants": [
            {{"name": "restaurant name", "cuisine": "cuisine type", "price_range": "$ or $$ or $$$"}}
        ],
        "activities": [
            {{"name": "activity name", "description": "brief description", "suggested_day": "day number or range"}}
        ],
        "events": [
            {{"name": "event name", "date": "date if known", "description": "brief description"}}
        ],
        "tips": [
            "tip 1", "tip 2", "tip 3"
        ]
    }}
    """

def get_fallback_recommendations(destination):
    """Provide static recommendations when OpenAI API is unavailable"""
    city_recommendations = {
        "Tokyo": {
            "attractions": [
                {"name": "Senso-ji Temple", "description": "Ancient Buddhist temple in Asakusa", "suggested_day": "1"},
                {"name": "Shibuya Crossing", "description": "World's busiest pedestrian crossing", "suggested_day": "1"},
                {"name": "Meiji Shrine", "description": "Serene Shinto shrine in a forest", "suggested_day": "2"},
                {"name": "Tokyo Skytree", "description": "Tallest structure in Japan with observation decks", "suggested_day": "2"},
                {"name": "Tsukiji Outer Market", "description": "Famous market with fresh seafood", "suggested_day": "3"}
            ],
            "restaurants": [
                {"name": "Sushi Dai", "cuisine": "Sushi", "price_range": "$$$"},
                {"name": "Ichiran Ramen", "cuisine": "Ramen", "price_range": "$$"},
                {"name": "Gonpachi Nishi-Azabu", "cuisine": "Japanese", "price_range": "$$"}
            ],
            "activities": [
                {"name": "Teamlab Borderless", "description": "Digital art museum", "suggested_day": "any"},
                {"name": "Yanaka Ginza", "description": "Traditional shopping street", "suggested_day": "any"}
            ],
            "events": [],
            "tips": [
                "Get a PASMO or Suica card for easy public transportation",
                "Many places are cash-only",
                "Download offline maps as some areas have limited connectivity"
            ]
        }
    }
    
    # Return default recommendations if city not found
    if destination not in city_recommendations:
        return {
            "attractions": [
                {"name": "Unable to provide specific recommendations", "description": "OpenAI API is currently unavailable", "suggested_day": "any"}
            ],
            "restaurants": [],
            "activities": [],
            "events": [],
            "tips": [
                "OpenAI API is currently unavailable",
                "Please try again later or check with local tourism websites",
                "Consider using Google Maps or TripAdvisor for current recommendations"
            ]
        }
    
    return city_recommendations[destination] 