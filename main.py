from utils import get_project_list
from github_operations import rename_github_repo
from dotenv import load_dotenv
import logging
import getpass
import gitlab
import shutil
import time
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

        # Define the full path to the log file
        timestamp = time.strftime("%Y%m%d%H%M%S")
        output_directory = f"output_{timestamp}"

        # Create the destination folder if it doesn't exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        log_filename = "my_log_file.log"
        log_file_path = os.path.join(output_directory, log_filename)

        # Define the full path to the success refactoring file
        sr_filename = "successful_refactoring.txt"
        sr_file_path = os.path.join(output_directory, sr_filename)

        # Define the full path to the failed refactoring file
        fr_filename = "failed_refactoring.txt"
        fr_file_path = os.path.join(output_directory, fr_filename)        

        # Create the output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Configure logging
        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')


        # Step 1: Get list of projects
        projects = get_project_list(project_list_file_path)

        for project in projects:

            print("########################################### Project ###########################################")
            old_gitlab_repo_url = project["old_gitlab_repo_url"]
            github_repo_url = project["github_repo_url"]
            new_repo_name = project["new_repo_name"]


            print(f"Old Gitlab Repo URL: {old_gitlab_repo_url}")
            print(f"Github Repo URL: {github_repo_url}")
            print(f"New Repo Name: {new_repo_name}")


            logging.info(f'########################################### {new_repo_name} ###########################################')
            logging.info(f'Old Gitlab Repo URL: {old_gitlab_repo_url}')
            logging.info(f'Github Repo URL: {github_repo_url}')



            # Step 2: Rename projects
            logging.info(f'Renaming Github Repo')
            # Extract the organization and repository name from the GitHub URL
            organization, repo_name = github_repo_url.split('/')[-2:]
            repo_name = repo_name.replace('.git', '')
            logging.info(f'Current Repo Name: {repo_name}')
            logging.info(f'New Repo Name: {new_repo_name}')
            had_error, error_message, response_message, new_github_repo_url = rename_github_repo(organization, repo_name, github_token, new_repo_name)
            if had_error:
                print(f"Error in renaming Github repo: {error_message}")
                logging.error(f"==> Error in renaming Github repo: {error_message}")
                with open(fr_file_path, "a") as file:
                    # Add the project URL to the list of failed refactoring projects.
                    file.write(gitlab_project_url + '\n')
                continue
            else:
                print(f"{response_message}")
                print(f"New Repo URL: {new_github_repo_url}")

    except ValueError as e:
        print("Error In parsing project-list file:", e)

      
if __name__ == "__main__":
    main()
