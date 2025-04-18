# This script is used to test the API endpoints of the Flask application.
curl -X GET http://localhost:8000/health


PR_NUMBER=3
REPO_NAME=sample-repository

FILE_NAME=$(date +%Y%m%d%H%M%S)_change_${REPO_NAME}_${PR_NUMBER}.md

curl https://raw.githubusercontent.com/saai-sudarsanan-swym/skyra-docs/refs/heads/main/feature_doc.md -o feature_doc.md
curl https://raw.githubusercontent.com/saai-sudarsanan-swym/skyra-docs/refs/heads/main/design_doc.md -o design_doc.md

# Generate Response
curl -X POST http://localhost:8000/generate \
  -F "feature_doc=@./feature_doc.md" \
  -F "design_doc=@./design_doc.md" \
  -F "data={\"repo\": \"${REPO_NAME}\", \"pr_number\": ${PR_NUMBER}}" \
  -H "Content-Type: multipart/form-data" -o ../frontend/src/${FILE_NAME}

echo "- [$(date +%Y%m%d%H%M%S)_change_${REPO_NAME}_${PR_NUMBER}](./${FILE_NAME})" >> ../frontend/src/SUMMARY.md
mdbook build ../frontend --dest-dir ../frontend/book
