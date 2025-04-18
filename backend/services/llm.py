import base64
from config import GEMINI_API_KEY
from google import generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)

def encode_file_to_base64(file_path):
    try:
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding {file_path}: {e}")
        return None

def send_files_and_get_response(prompt, file_paths):
    parts = [{"text": prompt}]
    for path in file_paths:
        encoded = encode_file_to_base64(path)
        if not encoded:
            return f"Failed to encode file: {path}"
        parts.append({
            "inline_data": {
                "mime_type": 'text/plain',
                "data": encoded
            }
        })

    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        response = model.generate_content(contents=[{"parts": parts}])
        return response.text
    except Exception as e:
        print(f"Model request error: {e}")
        return None
