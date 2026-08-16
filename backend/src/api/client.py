from utils.progress import retry_with_status, console
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
 
@retry_with_status(max_retries=5, initial_delay=10)
def gemini_api(prompt, userData):
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt, userData]
    )
    return response




