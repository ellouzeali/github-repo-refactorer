from utils import get_project_list
from github_operations import rename_github_repo
from dotenv import load_dotenv
import shutil
import time
import sys
import os

def main():
    print("RUNNING GITHUB-REPO-REFACTORER")

    # Load variables from .env file into environment variables
    load_dotenv()
    github_org_name = os.getenv("GITHUB_ORG_NAME")
    github_token = os.getenv("GITHUB_TOKEN")
    github_devops_repo_url = os.getenv("GITHUB_DEVOPS_REPO_URL")
    github_devops_repo_branch_name = os.getenv("GITHUB_DEVOPS_REPO_BRANCH_NAME")
    github_devops_repo_file_path = os.getenv("GITHUB_DEVOPS_REPO_FILE_PATH")
    project_list_file_path = os.getenv("PROJECT_LIST_FILE_PATH")

    # Check if all required environment variables are defined
    if None in (
        github_org_name,
        github_token,
        github_devops_repo_url,
        github_devops_repo_branch_name,
        github_devops_repo_file_path,
        project_list_file_path,
    ):
        print("One or more environment variables are missing.")
        sys.exit(1)
    try:
        had_error = False
        error_message = ""

        # Step 1: Get list of projects
        projects = get_project_list(project_list_file_path)

        for project in projects:
            print(project)

            # Step 2: Rename projects
            had_error, error_message, response_message, new_github_repo_url = rename_github_repo(project["github_repo_url"], github_token, project["new_repo_name"])
            if had_error:
                print(f"Error in renaming Github repo: {error_message}")
            else:
                print(f"{response_message}")
                print(f"New Repo URL: {new_github_repo_url}")

    except ValueError as e:
        print("Error In parsing project-list file:", e)

      
if __name__ == "__main__":
    main()
