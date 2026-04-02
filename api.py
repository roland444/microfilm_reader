from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

def gemini_api(prompt, userData):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt, userData]
        )
    
    return response




