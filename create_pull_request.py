import os
import getpass
from github import Github
from dotenv import load_dotenv


def create_github_pull_request(github_token, organization_name, repo_name, merge_request_obj, org_members):

    # Create instance of Github auth
    g = Github(github_token)

    try:
        print("Connection to github repo")

        # Get Github repo
        repo = g.get_repo(repo_name)
        
        print("Creating pull request")

        # Create pull request
        pull_request = repo.create_pull(
            title=merge_request_obj["title"],
            body=merge_request_obj["description"],
            base=merge_request_obj["target_branch"],
            head=merge_request_obj["source_branch"]
            # TODO uncomment in prod (it seems that drafted pull requests are not supported in the free Github plan)
            # draft=merge_request_obj["is_drafted"]
        )

        assignee = merge_request_obj["assignee"]
        if assignee and assignee != "None":

            print(f"Assignee: {assignee}")
            username = get_username_by_full_name(org_members, assignee)
            print(f"Username: {username}")

            if is_collaborator(repo, username):
                pull_request.add_to_assignees(username)
            else:
                print(f"Skipping assignee {assignee} as he is not a collaborator")

        reviewers = merge_request_obj["reviewers"]
        if reviewers and reviewers != []:
            for reviewer in reviewers:

                print(f"Reviewer: {reviewer}")
                username = get_username_by_full_name(org_members, reviewer)
                print(f"Username: {username}")                

                if is_collaborator(repo, username):
                    pull_request.create_review_request([username])
                else:
                    print(f"Skipping reviewer {reviewer} as he is not a collaborator")

        labels = merge_request_obj["labels"]
        if labels and labels != "None":
            labels = [label.strip() for label in labels.split(',')]
            pull_request.add_to_labels(*labels)

        milestone = merge_request_obj["milestone"]
        if milestone and milestone != "None":
            pull_request.set_milestone(milestone)

        # TODO verify existence
        # pull_request.set_time_tracking(time_estimate, time_spent)

        comments = merge_request_obj["comments"]
        if comments and comments != "None":
            for comment in comments:
                # Add each comment as a separate issue comment
                pull_request.create_issue_comment(comment)

        # Add Gitlab merge request urls as comment
        last_comment = f"Gitlab Merge Request URL: {merge_request_obj['url']}"
        pull_request.create_issue_comment(last_comment)

        # Return pull request URL
        return pull_request.html_url

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None



def is_collaborator(repo, username):
    """
    Check if a user is a collaborator of a GitHub repository.
    """
    collaborators = repo.get_collaborators()
    for collaborator in collaborators:
        if collaborator.login == username:
            return True
    return False


# def get_github_username(github, full_name):
#     users = github.search_users(full_name + " in:fullname")
#     for user in users:
#         return user.login
#     return None


# def get_username_by_full_name(github, organization_name, member_full_name):
    
#     # Get the organization
#     org = github.get_organization(organization_name)
    
#     # Get the members of the organization and filter by full name
#     for member in org.get_members():
#         if member.name == member_full_name:
#             return member.login
#     return None  # Return None if the member is not found


def get_username_by_full_name(members_list, user_full_name):
    try:
        if user_full_name:
            for member in members_list:
                if member["full_name"].lower() == user_full_name.lower():
                    return member["user_name"]
        return None  # Return None if the member is not found
    except Exception as e:
        return None


def get_organization_members(organization_name, github_token):
    # Authenticate to GitHub
    g = Github(github_token)
    
    # Get the organization
    org = g.get_organization(organization_name)
    
    # Initialize an empty list to store member details
    members_list = []
    
    # Get the members of the organization and create a list of dictionaries
    for member in org.get_members():
        member_details = {
            "full_name": member.name,
            "user_name": member.login
        }
        members_list.append(member_details)
    
    return members_list




# Usage Exemple
def main():
    # github_token = getpass.getpass("Enter your GITHUB_TOKEN: ")
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")

    repo_name = "ae-organization/charger"
    organization_name = "ae-organization"


    org_members = get_organization_members(organization_name, github_token)

    print(f"Members: {org_members}")

    mr_url = "https://gitlab.com/symphony-cloud/symphony-local/charge-station-gen3/charger/-/merge_requests/55"
    mr_id = "55"
    mr_title = "Added Test fkh/currentWatchdogImpl to antoine/add_central_module "
    mr_description = "Tes Description for pull request"
    mr_status = "opened"
    is_drafted = True
    source_branch = "fkh/currentWatchdogImpl"
    target_branch = "antoine/add_central_module"
    assignee = "ali ELLOUZE"
    reviewers = ["MariemEllouze", "Heni Ellouze", "fawzi KHABER"]
    labels = "sw0.8"
    milestone = "None"
    time_estimate = "0h"
    time_spent = "0h"
    mr_comments = ['Test comment 1', 'Test comment 2', 'Test comment 3']


    # Create a merge request object
    merge_request_obj = {
        "url": mr_url,
        "id": mr_id,
        "title": mr_title,
        "description": mr_description,
        "status": mr_status,
        "is_drafted": is_drafted,
        "source_branch": source_branch,
        "target_branch": target_branch,
        "assignee": assignee,
        "reviewers": reviewers,
        "labels": labels,
        "milestone": milestone,
        "time_estimate": time_estimate,
        "total_time_spent": time_spent,
        "comments": mr_comments
    }   

    pull_request_url = create_github_pull_request(github_token, organization_name, repo_name, merge_request_obj, org_members)

    if pull_request_url:
        print(f"Pull request was successfully created : {pull_request_url}")
    else:
        print("Failed to create pull request")

if __name__ == "__main__":
    main()