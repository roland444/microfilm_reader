from dotenv import load_dotenv
from google import genai
import time
import os

load_dotenv()

MAX_RETRIES = 5
INITIAL_DELAY = 10

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
 
def gemini_api(prompt, userData):
    delay = INITIAL_DELAY
 
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[prompt, userData]
            )
            return response
 
        except Exception as e:
            error_str = str(e)
 
            is_retryable = any(code in error_str for code in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"])
 
            if is_retryable and attempt < MAX_RETRIES:
                print(f"[Próba {attempt}/{MAX_RETRIES}] API niedostępne, ponowna próba za {delay}s... ({e})")
                time.sleep(delay)
                delay *= 2
            else:
                raise




