import requests
from config import GITHUB_TOKEN

def get_pr_details(owner, api_version, repo, pr_number, output_path):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": api_version
    }

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    pr_data = requests.get(f"{base_url}/pulls/{pr_number}", headers=headers).json()
    commits_data = requests.get(f"{base_url}/pulls/{pr_number}/commits", headers=headers).json()

    with open(output_path, 'w') as f:
        f.write(f"PR Title: {pr_data.get('title', 'N/A')}\n")
        f.write(f"PR Description:\n{pr_data.get('body', 'No description provided.')}\n")
        f.write("Commit Messages:\n")
        for idx, commit in enumerate(commits_data, 1):
            f.write(f"{idx}. {commit['commit']['message']}\n")
