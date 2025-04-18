# This script is used to test the API endpoints of the Flask application.
curl -X GET http://localhost:8000/health


PR_NUMBER=3
REPO_NAME=sample-repository

# Generate Response
curl -X POST http://localhost:8000/generate \
  -F "feature_doc=@./feature_doc.md" \
  -F "design_doc=@./design_doc.md" \
  -F "data={\"repo\": \"$REPO_NAME\", \"pr_number\": $PR_NUMBER}" \
  -H "Content-Type: multipart/form-data" -o frontend/src/$(date +%Y%m%d%H%M%S)_change_$REPO_NAME_$PR_NUMBER.md