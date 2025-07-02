import os
from dotenv import load_dotenv
import google.generativeai as genai 

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise EnvironmentError("❌ GOOGLE_API_KEY missing from .env")

genai.configure(api_key=api_key)

for model in genai.list_models():
    print(model.name, model.supported_generation_methods)
