import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API")

if not API_KEY:
    raise RuntimeError("Missing GEMINI_API in .env")

client = genai.Client(api_key=API_KEY)

print("Uploading video...")
video_file = client.files.upload(file="video2.mp4")

print("Uploaded. Waiting for processing...")

while True:
    file_info = client.files.get(name=video_file.name)  # 正确查询
    state = file_info.state.name
    print("File state:", state)

    if state == "ACTIVE":
        print("File is ready.")
        break
    elif state == "FAILED":
        raise RuntimeError("File processing failed.")

    time.sleep(2)

prompt = """
Analyze this video and list every distinct object that appears.
For each object, give timestamps (MM:SS).
Return JSON.
"""

response = client.models.generate_content(
    model="models/gemini-3-flash-preview",
    contents=[video_file, types.Part(text=prompt)]
)

print("\n===== Detected Objects =====\n")
print(response.text)
