import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_learning_path(goal, time_available_per_week, prior_experience):
    """
    Generate a personalized learning path using Gemini AI
    """
    try:
        # Configure Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Create a comprehensive personalized learning path for the following:
        - Goal: {goal}
        - Time available per week: {time_available_per_week} hours
        - Prior experience: {prior_experience}
        
        Create a detailed week-by-week learning plan with at least 4-8 weeks. Each week should build upon the previous one.
        
        Please provide a structured learning plan in the following JSON format:
        {{
            "duration": "X weeks",
            "phases": [
                {{
                    "week": 1,
                    "topics": ["topic1", "topic2"],
                    "resources": ["resource1", "resource2"],
                    "time": "{time_available_per_week} hours"
                }},
                {{
                    "week": 2,
                    "topics": ["topic3", "topic4"],
                    "resources": ["resource3", "resource4"],
                    "time": "{time_available_per_week} hours"
                }}
            ]
        }}
        
        Important: 
        1. Include multiple weeks (at least 4-8 weeks)
        2. Make sure each week builds on previous knowledge
        3. Provide practical resources for each week
        4. Return ONLY valid JSON, no additional text or markdown
        """
        
        response = model.generate_content(prompt)
        raw_response = response.text.strip()
        
        # Clean the response to extract JSON
        # Remove markdown code blocks if present
        if raw_response.startswith('```json'):
            raw_response = raw_response[7:]  # Remove ```json
        if raw_response.startswith('```'):
            raw_response = raw_response[3:]   # Remove ```
        if raw_response.endswith('```'):
            raw_response = raw_response[:-3]  # Remove closing ```
        
        raw_response = raw_response.strip()
        
        # Validate JSON before returning
        try:
            json.loads(raw_response)
            return raw_response
        except json.JSONDecodeError:
            print(f"Warning: Gemini returned invalid JSON. Raw response: {raw_response[:200]}...")
            # Fall through to fallback response
        
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        # Return a fallback response with multiple weeks if API fails
        fallback_response = {
            "duration": "6 weeks",
            "phases": [
                {
                    "week": 1,
                    "topics": [f"Getting started with {goal}", "Basic concepts and setup"],
                    "resources": ["Official documentation", "YouTube tutorials"],
                    "time": f"{time_available_per_week} hours"
                },
                {
                    "week": 2,
                    "topics": [f"Intermediate {goal} concepts", "Hands-on practice"],
                    "resources": ["Online courses", "Practice exercises"],
                    "time": f"{time_available_per_week} hours"
                },
                {
                    "week": 3,
                    "topics": [f"Advanced {goal} topics", "Real-world applications"],
                    "resources": ["Advanced tutorials", "Project examples"],
                    "time": f"{time_available_per_week} hours"
                },
                {
                    "week": 4,
                    "topics": ["Building your first project", "Best practices"],
                    "resources": ["Project guides", "Community forums"],
                    "time": f"{time_available_per_week} hours"
                },
                {
                    "week": 5,
                    "topics": ["Testing and debugging", "Code optimization"],
                    "resources": ["Testing frameworks", "Debugging tools"],
                    "time": f"{time_available_per_week} hours"
                },
                {
                    "week": 6,
                    "topics": ["Final project", "Portfolio development"],
                    "resources": ["Portfolio examples", "Deployment guides"],
                    "time": f"{time_available_per_week} hours"
                }
            ]
        }
        return json.dumps(fallback_response)
