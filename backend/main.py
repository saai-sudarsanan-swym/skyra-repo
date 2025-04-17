from dotenv import load_dotenv
import os
import requests
from google import generativeai as genai
load_dotenv()
import base64
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

api_key = os.getenv('GEMINI_API_KEY','xxx')
github_token = os.getenv('GITHUB_TOKEN','xxx')

genai.configure(api_key=api_key)

def get_pr_details(OWNER, API_VERSION, REPO, PR_NUMBER) -> dict:
    """Fetches PR details from the GitHub API."""
    # Retrieve GitHub token from environment variable
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise EnvironmentError("Please set the GITHUB_TOKEN environment variable.")

    # Headers for authentication and API versioning
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION
    }

    # Base URL for GitHub API
    BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"

    # Fetch PR details
    pr_url = f"{BASE_URL}/pulls/{PR_NUMBER}"
    pr_response = requests.get(pr_url, headers=headers)
    pr_response.raise_for_status()
    pr_data = pr_response.json()

    # Extract PR title and description
    pr_title = pr_data.get("title", "N/A")
    pr_description = pr_data.get("body", "No description provided.")

    # Fetch commits associated with the PR
    commits_url = f"{BASE_URL}/pulls/{PR_NUMBER}/commits"
    commits_response = requests.get(commits_url, headers=headers)
    commits_response.raise_for_status()
    commits_data = commits_response.json()

    # Extract commit messages
    commit_messages = [commit["commit"]["message"] for commit in commits_data]
    with open('input/pr_details','w') as f:
        f.write(f"PR Title: {pr_title}\n")
        f.write(f"PR Description:\n{pr_description}\n")
        f.write("Commit Messages:")
        for idx, message in enumerate(commit_messages, 1):
            f.write(f"{idx}. {message}\n")

def get_llm_response(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        response = model.generate_content(
            contents=[{"parts": [{"text": prompt}]}]
        )
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def encode_file_to_base64(file_path: str) -> str:
    """Encodes a file to Base64."""
    try:
        with open(file_path, "rb") as file:
            encoded_string = base64.b64encode(file.read()).decode("utf-8")
            return encoded_string
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred during file encoding: {e}")
        return None

def send_files_and_get_response(prompt: str, file_paths: list) -> str:
    """Sends multiple files along with a prompt to the Gemini model."""
    parts = [{"text": prompt}]
    for file_path in file_paths:
        encoded_file = encode_file_to_base64(file_path)
        if not encoded_file:
            return f"Failed to encode file: {file_path}"
        parts.append({
            "inline_data": {
                "mime_type": 'text/plain',
                "data": encoded_file
            }
        })
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        response = model.generate_content(
            contents=[{"parts": parts}]
        )
        return response.text
    except Exception as e:
        print(f"An error occurred while sending files: {e}")
        return None

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'input')
ALLOWED_EXTENSIONS = {'md'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'feature_doc' not in request.files or 'design_doc' not in request.files:
        return jsonify({'error': 'Both feature_doc and design_doc files are required.'}), 400

    feature_doc = request.files['feature_doc']
    design_doc = request.files['design_doc']

    if feature_doc.filename == '' or design_doc.filename == '':
        return jsonify({'error': 'No selected file(s).'}), 400

    if not (allowed_file(feature_doc.filename) and allowed_file(design_doc.filename)):
        return jsonify({'error': 'Only .md files are allowed.'}), 400

    # Save the files
    feature_doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'feature_doc.md')
    design_doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'design_doc.md')
    feature_doc.save(feature_doc_path)
    design_doc.save(design_doc_path)

    return jsonify({'message': 'Files uploaded successfully.'}), 200

@app.route('/generate', methods=['POST'])
def generate_docs():
    # Check if the files exist
    feature_doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'feature_doc.md')
    design_doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'design_doc.md')

    if not os.path.exists(feature_doc_path) or not os.path.exists(design_doc_path):
        return jsonify({'error': 'Feature doc or design doc file not found.'}), 404

    # Parse the POST request JSON data
    data = request.get_json()
    if not data or 'repo' not in data or 'pr_number' not in data:
        return jsonify({'error': 'Repository name and PR number are required.'}), 400

    REPO = data['repo']
    PR_NUMBER = data['pr_number']

    # Read the prompt
    with open('prompt.txt', 'r') as f:
        file_prompt = f.read()

    OWNER = 'swym-corp'
    API_VERSION = "2022-11-28"
    get_pr_details(OWNER, API_VERSION, REPO, PR_NUMBER)

    # Generate response
    response = send_files_and_get_response(file_prompt, [feature_doc_path, design_doc_path])
    if response:
        return jsonify({'response': response}), 200
    else:
        return jsonify({'error': 'Failed to generate response.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
