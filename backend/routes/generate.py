import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from config import OWNER, API_VERSION
from services.github import get_pr_details, generate_pr_diff
from services.utils import allowed_file
from services.llm import send_files_and_get_response
import json

# Define the permanent upload directory
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

generate_bp = Blueprint('generate', __name__)

@generate_bp.route('/generate', methods=['POST', 'OPTIONS'])
def generate_docs():
    if request.method == 'OPTIONS':
        return '', 204

    # Step 1: Handle file upload
    if 'feature_doc' not in request.files or 'design_doc' not in request.files:
        return jsonify({'error': 'Both feature_doc and design_doc are required.'}), 400

    feature_doc = request.files['feature_doc']
    design_doc = request.files['design_doc']

    if not (feature_doc.filename and design_doc.filename):
        return jsonify({'error': 'One or both files are missing.'}), 400

    # Check if files are of allowed type
    if not (allowed_file(feature_doc.filename) and allowed_file(design_doc.filename)):
        return jsonify({'error': 'Only .md files are allowed.'}), 400

    # Save the files in the uploads directory
    feature_doc_path = os.path.join(UPLOAD_FOLDER, secure_filename('feature_doc.md'))
    design_doc_path = os.path.join(UPLOAD_FOLDER, secure_filename('design_doc.md'))

    feature_doc.save(feature_doc_path)
    design_doc.save(design_doc_path)

    # Step 2: Process PR details and generate documentation
    data_str = request.form.get('data')
    if data_str:
        data = json.loads(data_str)  # Convert string to JSON object
    else:
        return jsonify({'error': 'Missing or malformed data.'}), 400

    repo = data['repo']
    pr_number = data['pr_number']

    pr_details_path = os.path.join(UPLOAD_FOLDER, 'pr_details.txt')
    pr_diff_path = os.path.join(UPLOAD_FOLDER, 'pr_diff.txt')

    # Fetch PR details
    get_pr_details(OWNER, API_VERSION, repo, pr_number, pr_details_path)
    generate_pr_diff(OWNER, API_VERSION, repo, pr_number, pr_diff_path)
    
    try:
        with open('prompt.txt', 'r') as f:
            prompt = f.read()
    except FileNotFoundError:
        return jsonify({'error': 'Prompt file not found.'}), 500

    # Get the response from the LLM
    response = send_files_and_get_response(prompt, [feature_doc_path, design_doc_path, pr_details_path])

    if not response:
        return jsonify({'error': 'LLM generation failed.'}), 500

    # Step 3: Save the generated documentation to a file
    output_file_path = os.path.join(UPLOAD_FOLDER, 'generated_documentation.txt')

    with open(output_file_path, 'w') as output_file:
        output_file.write(response)

    # Step 4: Return the generated file as a download
    return send_file(output_file_path, as_attachment=True, download_name='generated_documentation.txt', mimetype='text/plain')
