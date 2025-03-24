import os
from openai import OpenAI
import json
from datetime import date

def get_env_var(key, default=None):
    value = os.environ.get(key, default)
    if value is None or value.strip() == '':
        raise ValueError(f"Missing required environment variable: {key}")
    return value.strip()

# Initialize the OpenAI client with better error handling
try:
    api_key = get_env_var('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY cannot be empty")
    client = OpenAI(api_key=api_key)
except ValueError as e:
    print(f"❌ Error initializing OpenAI client: {e}")
    print("Please ensure OPENAI_API_KEY is properly set in your environment")
    raise

def get_recommendations(destination, start_date, end_date):

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
    
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful travel assistant that provides detailed recommendations in JSON format."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    
    # Extract and parse the response
    result = response.choices[0].message.content
    
    # Clean up the response to ensure it's valid JSON
    # Remove any markdown code block syntax and trim whitespace
    result = result.replace("```json", "").replace("```", "").strip()
    
    try:
        # Parse the JSON response
        recommendations = json.loads(result)
        return recommendations
    except json.JSONDecodeError:
        # If parsing fails, return a simple error object
        return {"error": "Failed to parse recommendations", "raw_response": result} 