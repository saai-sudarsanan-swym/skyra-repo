# This script is used to test the API endpoints of the Flask application.
curl -X GET http://localhost:8000/health

# Generate Response
curl -X POST http://localhost:8000/generate \
  -F "feature_doc=@./feature_doc.md" \
  -F "design_doc=@./design_doc.md" \
  -F "data={\"repo\": \"sample-repository\", \"pr_number\": 3}" \
  -H "Content-Type: multipart/form-data"