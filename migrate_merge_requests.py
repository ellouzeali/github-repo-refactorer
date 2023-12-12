import os
import sys
import time
import gitlab
import getpass
import logging
from github import Github
from dotenv import load_dotenv
from utils import get_project_list, extract_repository_path
from get_merge_request import get_merge_requests_for_private_project
from create_pull_request import create_github_pull_request, get_organization_members




# Example usage
def main():


    gitlab_url = "https://gitlab.com"
    # gitlab_token = getpass.getpass("Enter your GITLAB_TOKEN: ")
    load_dotenv()
    gitlab_token = os.getenv("GITLAB_TOKEN")
    github_token = os.getenv("GITHUB_TOKEN")
    organization_name = os.getenv("GITHUB_ORG_NAME")
    members_file_path = os.getenv("MEMBER_LIST_FILE_PATH")
    project_list_file_path = os.getenv("PROJECT_LIST_FILE_PATH")
    
    # Check if all required environment variables are defined
    if None in (
        gitlab_token,
        github_token,
        organization_name,
        members_file_path,
        project_list_file_path,
    ):
        print("One or more environment variables are missing.")
        sys.exit(1)


    # Define the full path to the log file
    timestamp = time.strftime("%Y%m%d%H%M%S")
    output_directory = f"mr_migration_output_{timestamp}"

    # Create the destination folder if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    log_filename = "my_log_file.log"
    log_file_path = os.path.join(output_directory, log_filename)

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


        print(f"Old Gitlab Repo URL: {old_gitlab_repo_url}")
        print(f"Github Repo URL: {github_repo_url}")

        # Extract the current repository name from the GitHub URL
        repo_name = github_repo_url.split('/')[-1].replace(".git", "")

        gitlab_repo_path = extract_repository_path (old_gitlab_repo_url)
        github_repo_path = extract_repository_path (github_repo_url)

        logging.info(f'########################################### {repo_name} ###########################################')
        logging.info(f'Gitlab Repo Path: {gitlab_repo_path}')
        logging.info(f'Github Repo Path: {github_repo_path}')


        # gitlab_repo_path = "test-migration-al105/testmigrationproject-al105"
        # github_repo_path = "TotalEnergiesCodeDev/testmigrationproject-al105"

        # gitlab_repo_path = "symphony-cloud/user-experience/guis/g2smart-angular"
        # github_repo_path = "ae-organization/g2smart-angular"

        # symphony-cloud/symphony-local/charge-station-gen3/charger
        # symphony-cloud/user-experience/guis/g2smart-angular
        # symphony-cloud/infrastructure/core/infra-manager.git"
        merge_requests = get_merge_requests_for_private_project(gitlab_url, gitlab_token, gitlab_repo_path)


        org_members = get_organization_members(members_file_path)

        print("===> Merge Requests: ")
        for merge_request_obj in merge_requests:
            print(f"******************************* Merge Request ID: {merge_request_obj['id']} *****************************************")
            print(f"URL: {merge_request_obj['url']}")
            print(f"Title: {merge_request_obj['title']}")
            print(f"Description: {merge_request_obj['description']}")
            print(f"Status: {merge_request_obj['status']}")
            print(f"Is Drafted: {merge_request_obj['is_drafted']}")
            print(f"Source Branch: {merge_request_obj['source_branch']}")
            print(f"Target Branch: {merge_request_obj['target_branch']}")
            print(f"Assignee: {merge_request_obj['assignee']}")
            print(f"Reviewers: {', '.join(merge_request_obj['reviewers'])}")
            print(f"Labels: {', '.join(merge_request_obj['labels'])}")
            print(f"Milestone: {merge_request_obj['milestone']}")
            print(f"Time Estimate: {merge_request_obj['time_estimate']}h")
            print(f"Time Spent: {merge_request_obj['total_time_spent']}h")
            # print(f"Comments: {merge_request_obj['comments']}")
            print("\n")

            pull_request_url = create_github_pull_request(github_token, organization_name, github_repo_path, merge_request_obj, org_members)

            if pull_request_url:
                print(f"Pull request was successfully created : {pull_request_url}")
            else:
                print("Failed to create pull request")


if __name__ == "__main__":
    main()