import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}")
genai.configure(api_key=api_key)

for m in genai.list_models():
    if "embedContent" in m.supported_generation_methods:
        print(f"Supported embedding model: {m.name}")
