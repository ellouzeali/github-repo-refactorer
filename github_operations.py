import requests

def rename_github_repo(owner, repo_name, github_token, new_name):
    had_error = False
    error_message = ""
    response_message = ""
    new_github_url = ""

    try:
        if repo_name == new_name:
            print(f"Ignore renaming repo {owner}/{repo_name}")
            response_message = response_message + f"Ignore renaming repo {owner}/{repo_name} \n"
            new_github_url = f'https://github.com/{owner}/{repo_name}.git'
        else:
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
                    response_message = response_message + f"Repository {owner}/{repo_name} has been renamed to {owner}/{new_name} \n"
                    new_github_url = f'https://github.com/{owner}/{new_name}.git'
                else:
                    print(f"Failed to rename the repository. Status code: {response.status_code}") 
                    had_error = True
                    error_message = error_message + f"Failed to rename the repository. Status code: {response.status_code} \n"
            else:
                print(f"Repository {owner}/{repo_name} does not exist or you do not have permission to access it.")
                had_error = True
                error_message = error_message + f"Repository {owner}/{repo_name} does not exist or you do not have permission to access it. \n"


    except Exception as e:
        print(f"***rename_github_repo*** An unexpected error occurred: {e}")
        had_error = True
        error_message = error_message + f"===> An unexpected error occurred: {e} \n"
    finally:
        return had_error, error_message, response_message, new_github_url


# Example usage
def main():
    github_repo_url = 'https://github.com/a-ellouze/b2c-tde-bridge.git'
    github_token = 'GITHUB_TOKEN'
    new_name = 'new-repo-name'
    rename_github_repo(github_repo_url, github_token, new_name)

if __name__ == "__main__":
    main()