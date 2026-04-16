import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

client = genai.Client(api_key=GEMINI_API_KEY)