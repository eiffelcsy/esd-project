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
        logger.error("Failed to initialize OpenAI client, returning error response")
        return {
            "error": "OpenAI API key not configured properly",
            "attractions": [],
            "restaurants": [],
            "activities": [],
            "events": [],
            "tips": ["OpenAI API is not configured properly. Please check your environment variables."]
        }

    # Calculate trip duration
    trip_duration = (end_date - start_date).days + 1
    
    # Create prompt for OpenAI
    prompt = f"""
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
    
    try:
        # Call OpenAI API
        logger.info("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant that provides detailed recommendations in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # Extract and parse the response
        result = response.choices[0].message.content
        logger.info("Received response from OpenAI API")
        
        # Clean up the response to ensure it's valid JSON
        # Remove any markdown code block syntax and trim whitespace
        result = result.replace("```json", "").replace("```", "").strip()
        
        try:
            # Parse the JSON response
            recommendations = json.loads(result)
            logger.info("Successfully parsed OpenAI response")
            return recommendations
        except json.JSONDecodeError as e:
            # If parsing fails, return a simple error object
            logger.error(f"Failed to parse OpenAI response: {e}")
            return {"error": "Failed to parse recommendations", "raw_response": result}
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return {
            "error": f"Failed to get recommendations from OpenAI: {str(e)}",
            "attractions": [],
            "restaurants": [],
            "activities": [],
            "events": [],
            "tips": [f"Error: {str(e)}"]
        } 