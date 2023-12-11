import os
import gitlab
import getpass
from github import Github
from dotenv import load_dotenv
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
    members_file_path = 'members-list.txt'


    # TODO recupare dynamic list of prject
    # gitlab_project_name = "test-migration-al105/testmigrationproject-al105"
    # github_project_name = "TotalEnergiesCodeDev/testmigrationproject-al105"

    gitlab_project_name = "symphony-cloud/user-experience/guis/g2smart-angular"
    github_project_name = "ae-organization/g2smart-angular"

    # symphony-cloud/symphony-local/charge-station-gen3/charger
    # symphony-cloud/user-experience/guis/g2smart-angular
    # symphony-cloud/infrastructure/core/infra-manager.git"
    merge_requests = get_merge_requests_for_private_project(gitlab_url, gitlab_token, gitlab_project_name)


    # Reverse the order of merge requests
    merge_requests = reversed(merge_requests)


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
        print(f"Comments: {merge_request_obj['comments']}")
        print("\n")

        pull_request_url = create_github_pull_request(github_token, organization_name, github_project_name, merge_request_obj, org_members)

        if pull_request_url:
            print(f"Pull request was successfully created : {pull_request_url}")
        else:
            print("Failed to create pull request")


if __name__ == "__main__":
    main()