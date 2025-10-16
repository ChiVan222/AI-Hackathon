import os
from dotenv import load_dotenv
from google import genai  
import re
import json

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)  
def extract_json_from_text(text: str):
    """
    Extract JSON code block from model output, if wrapped in markdown (```json ... ```).
    """
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        text = match.group(1)
    text = text.strip()
    return text

async def call_llm(prompt: str):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    text = response.text or ""

    try:
        cleaned = extract_json_from_text(text)
        data = json.loads(cleaned)
        return data 
    except Exception as e:
        print(f"[WARN] Failed to parse JSON: {e}")
        return {"raw_output": text}
    
