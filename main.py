from utils import get_project_list
from github_operations import rename_github_repo
from replace_url_operations import update_scm_connections_in_maven_repositories, update_azure_devops_services
from dotenv import load_dotenv
import logging
import getpass
import gitlab
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
        had_issue = False
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

        # Define the full path to the failed refactoring file
        warning_filename = "partial_success_refactoring.txt"
        warning_file_path = os.path.join(output_directory, warning_filename)                

        # Define the full path to the updated AZ Devops services
        az_services_filename = "updated_az_devops_services.txt"
        az_services_file_path = os.path.join(output_directory, az_services_filename) 

        # Create the output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Configure logging
        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')


        # Get list of projects
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



            # Step 1: Rename projects
            logging.info('*************** Step 1: Renaming Github Repo ***************')
            print('*************** Step 1: Renaming Github Repo ***************')

            # Extract the current repository name from the GitHub URL
            repo_name = github_repo_url.split('/')[-1].replace(".git", "")
            logging.info(f'Current Repo Name: {repo_name}')
            logging.info(f'New Repo Name: {new_repo_name}')
            had_error, error_message, response_message, new_github_repo_url = rename_github_repo(github_org_name, repo_name, github_token, new_repo_name)
            if had_error:
                print(f"Error in renaming Github repo: {error_message}")
                logging.error(f"==> Error in renaming Github repo: {error_message}")
                with open(fr_file_path, "a") as file:
                    # Add the project URL to the list of failed refactoring projects.
                    file.write(github_repo_url + '\n')
                continue
            else:
                print(f"{response_message}")
                print(f"New Repo URL: {new_github_repo_url}")
                logging.info(f'{response_message}')
                logging.info(f'New Repo URL: {new_github_repo_url}')


            # Step 2: Change repository URL inside pom.xml file and commit the changes
            logging.info(f'*************** Step 2: Update pom.xml files if exists ***************')
            print('*************** Step 2: Update pom.xml files if exists ***************')

            github_project_path_segment = "/".join([github_org_name, new_repo_name])

            logging.info(f'Github Project Path Segment: {github_project_path_segment}')
            print(f"Github Project Path Segment: {github_project_path_segment}")

            had_error, error_message = update_scm_connections_in_maven_repositories(new_github_repo_url, github_token, github_project_path_segment)
            if had_error:
                logging.error(error_message)
                had_issue = True                          
            else:
                logging.info(f'SCM connections were successfully updated in the pom files')


            # Step 3: Change repository URL inside the CI/CD project
            logging.info(f'*************** Step 3: Change repository URL inside the CI/CD project***************')
            print('*************** Step 3: Change repository URL inside the CI/CD project***************')

            # Remove the ".git" from the Url
            old_repo_url = old_gitlab_repo_url.replace('.git', '')
            new_repo_url = new_github_repo_url.replace('.git', '')
            logging.info(f'Old Gitlab Repo URL: {old_repo_url}')
            logging.info(f'New Github Repo URL: {new_repo_url}')

            had_error, error_message, changed_services = update_azure_devops_services (github_devops_repo_url, github_token, github_devops_repo_branch_name, github_devops_repo_file_path, old_repo_url, new_repo_url)
            if had_error:
                logging.error(error_message)
                had_issue = True
            else:
                logging.info(f'Repository URL was successfully updated in the CI/CD config File')
                logging.info(f'AZ Devops services updated are: {changed_services}')       

            if changed_services:
                with open(az_services_file_path, "a") as file:
                    # Save updated services of infra-as-code project
                    file.write('\n'.join(changed_services))                   
                    file.write('\n')


            if had_issue:
                print(f"{repo_name} has been renamed but encountered some issues in updating Urls!!")
                logging.info(f'Warning!! {repo_name} has been renamed but encountered some issues')
                with open(warning_file_path, "a") as file:
                    # Add the project URL to the list of partial success migration projects.
                    file.write(new_github_repo_url + '\n')     
            else :
                print(f"{repo_name} has been successfully refactored")
                logging.info(f'{repo_name} has been successfully refactored')
                with open(sr_file_path, "a") as file:
                    # Add the project URL to the list of successful migration projects.
                    file.write(new_github_repo_url + '\n')  




        # Close the log file
        logging.shutdown()

    except ValueError as e:
        print("Error In parsing project-list file:", e)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)




if __name__ == "__main__":
    main()
