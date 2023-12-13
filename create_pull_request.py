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
        if labels and labels != []:
            # labels = [label.strip() for label in labels.split(',')]
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


def get_organization_members(file_path):
    # Initialize an empty list to store member details
    members_list = []

    try:
        # Read the members-list.txt file
        with open(file_path, 'r') as file:
            # Skip the header line
            header = file.readline()
            # Iterate through the remaining lines
            for line_number, line in enumerate(file, start=2):  # Start line numbering from 2 (skipping header)
                try:
                    # Split the line into full name and username
                    full_name, user_name = line.strip().split('\t')
                    # Create a dictionary for each member
                    member_details = {
                        "full_name": full_name,
                        "user_name": user_name
                    }
                    # Append the member details to the list
                    members_list.append(member_details)
                except ValueError:
                    # Handle improper line formatting (e.g., not enough values to unpack)
                    print(f"Error in line {line_number}: Improper line formatting")
                    raise ValueError(f"Error in line {line_number}: Improper line formatting")
    except FileNotFoundError:
        # Handle file not found error
        print(f"Error: File not found - {file_path}")
        raise FileNotFoundError(f"Error: File not found - {file_path}")
    except Exception as e:
        # Handle other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise Exception(f"An unexpected error occurred: {e}")

    return members_list





# Usage Exemple
def main():
    # github_token = getpass.getpass("Enter your GITHUB_TOKEN: ")
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")

    repo_name = "ae-organization/charger"
    organization_name = "ae-organization"
    members_file_path = 'members-list.txt'


    org_members = get_organization_members(members_file_path)

    print(f"Members: {org_members}")

    mr_url = "https://gitlab.com/symphony-cloud/symphony-local/charge-station-gen3/charger/-/merge_requests/102"
    mr_id = "102"
    mr_title = "feature(dbus_server): Dbus server lib with the Evse"
    mr_description = """Voici une proposition d'implem d'un server DBus. 
    - Ce n'est absolument pas testé, je ferais ça à mon retour. 
    - il y a clairement du code à factoriser et a passer sous qtoverload, je ferais ça une fois testé.
        -> Mais ça compile, et vous pouvez jeter un oeil si ça vous intéresse. 
    - Pour ce qui est de l'archi, dites moi si ça vous va: Je pensais faire une lib dbus_client par la suite. La lib interface introduite ici serait utilisé comme api de la lib dbus_client, ce qui nous permetras d'avoir la même api que dans la lib monitoring."""
    mr_status = "opened"
    is_drafted = False
    source_branch = "jon/dbus/evse-interface"
    target_branch = "0.9"
    assignee = "ali ELLOUZE"
    reviewers = ["Mariem Ellouze", "Heni Ellouze", "fawzi KHABER"]
    labels = ["sw0.9", "test"]
    milestone = "None"
    time_estimate = "0h"
    time_spent = "0h"
    mr_comments = ['assigned to @jonpetri', 'added 5 commits\n\n<ul><li>e67d79e2 - Fix Fextender driver</li><li>e8cd015f - Invert msb/lsb Temperature value</li><li>3b420971 - build: Ignore -Weffc++ on some qt headers</li><li>f62acd49 - refactor(interface): Evse interface definition</li><li>fee872ef - feature(dbus_server): Dbus server lib with the Evse</li></ul>\n\n[Compare with previous version](/symphony-cloud/symphony-local/charge-station-gen3/charger/-/merge_requests/102/diffs?diff_id=862244625&start_sha=bb75c2334a297677e38d0351b67f5354f02a766c)', 'approved this merge request', 'approved this merge request']


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