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

def get_pr_diff(owner, api_version, repo, pr_number, output_path):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.patch",
        "X-GitHub-Api-Version": api_version
    }
    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    diff_url = f"{base_url}/pulls/{pr_number}"
    response = requests.get(diff_url, headers=headers)

    with open(output_path, 'w') as f:
        f.write(response.text)
    if response.status_code == 200:
        print(f"Diff saved to {output_path}")
    else:
        print(f"Failed to fetch diff: {response.status_code} - {response.text}")