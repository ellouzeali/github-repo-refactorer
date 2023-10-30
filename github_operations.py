import requests

def rename_github_repo(github_repo_url, github_token, new_name):
    # Extract the owner and repository name from the GitHub URL
    owner, repo_name = github_repo_url.split('/')[-2:]

    # Construct the API URLs
    repo_exists_url = f'https://api.github.com/repos/{owner}/{repo_name}'
    rename_repo_url = f'https://api.github.com/repos/{owner}/{repo_name}'

    # Set up headers with the GitHub token
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Check if the repository exists
    response = requests.get(repo_exists_url, headers=headers)

    if response.status_code == 200:
        # Repository exists, proceed to rename
        data = {
            "name": new_name
        }
        response = requests.patch(rename_repo_url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"Repository {owner}/{repo_name} has been renamed to {owner}/{new_name}")
        else:
            print(f"Failed to rename the repository. Status code: {response.status_code}")
    else:
        print(f"Repository {owner}/{repo_name} does not exist or you do not have permission to access it.")



# Example usage
def main():
    github_repo_url = 'https://github.com/a-ellouze/b2c-tde-bridge.git'
    github_token = 'GITHUB_TOKEN'
    new_name = 'new-repo-name'
    rename_github_repo(github_repo_url, github_token, new_name)

if __name__ == "__main__":
    main()