import gitlab
import os
import getpass


def get_merge_requests_for_private_project(gitlab_url, gitlab_token, project_name_with_namespace):
    merge_requests_list = []  # Create a list to store merge request objects

    print("Connecting to Gitlab")

    try:
        # Step 1: Create a Gitlab API client
        gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        
        # Authenticate with the Gitlab API
        gl.auth()
        
        # Fetch the project by its URL
        project = gl.projects.get(project_name_with_namespace)

        print(f"Fetching merge requests for project: {project.name}")
                
        # Get merge requests for the project with pagination
        # The project.mergerequests.list() function gets only the last 20 merge requests due to the default pagination behavior of the GitLab API
        page = 1
        merge_requests = []
        while True:
            page_merge_requests = project.mergerequests.list(state='opened', page=page, per_page=100)  # Adjust per_page as needed
            if not page_merge_requests:
                break
            merge_requests.extend(page_merge_requests)
            page += 1

        # Create a text file for each project
        for merge_request in merge_requests:
            mr_url = merge_request.web_url
            mr_id = merge_request.iid
            mr_title = merge_request.title
            mr_description = merge_request.description
            mr_status = merge_request.state
            is_drafted = merge_request.work_in_progress
            source_branch = merge_request.source_branch
            target_branch = merge_request.target_branch
            assignee = merge_request.assignee["name"] if merge_request.assignee else "None"
            reviewers = [reviewer["name"] for reviewer in merge_request.reviewers] if merge_request.reviewers else "None"
            # TODO verify why some mr labels are printed "N,o,n,e" and not "None"
            labels = merge_request.labels if merge_request.labels else "None"
            milestone = merge_request.milestone["title"] if merge_request.milestone else "None"
            # TODO: Verify the existence of Time Tracking in GitLab Merge Requests
            time_tracking = {
                "time_estimate": merge_request.time_stats()["time_estimate"],
                "total_time_spent": merge_request.time_stats()["total_time_spent"]
            }
            mr_comments = []
            notes_list = merge_request.notes.list()
            if notes_list:
                for note in notes_list:
                    mr_comments.append(f"{note.body}") 
             

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
                "time_estimate": time_tracking["time_estimate"],
                "total_time_spent": time_tracking["total_time_spent"],
                "comments": mr_comments
            }            
            merge_requests_list.append(merge_request_obj)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return merge_requests_list

# Example usage
def main():


    gitlab_url = "https://gitlab.com"
    # private_token = getpass.getpass("Enter your GITLAB_TOKEN: ")
    load_dotenv()
    gitlab_token = os.getenv("GITLAB_TOKEN")
    
    project_name_with_namespace = "symphony-cloud/symphony-local/charge-station-gen3/charger"
    # symphony-cloud/user-experience/guis/g2smart-angular
    # symphony-cloud/infrastructure/core/infra-manager.git"
    merge_requests = get_merge_requests_for_private_project(gitlab_url, private_token, project_name_with_namespace)

    print("===> Merge Requests: ")
    for mr in merge_requests:
        print(f"******************************* Merge Request ID: {mr['id']} *****************************************")
        print(f"URL: {mr['url']}")
        print(f"Title: {mr['title']}")
        print(f"Description: {mr['description']}")
        print(f"Status: {mr['status']}")
        print(f"Is Drafted: {mr['is_drafted']}")
        print(f"Source Branch: {mr['source_branch']}")
        print(f"Target Branch: {mr['target_branch']}")
        print(f"Assignee: {mr['assignee']}")
        print(f"Reviewers: {', '.join(mr['reviewers'])}")
        print(f"Labels: {', '.join(mr['labels'])}")
        print(f"Milestone: {mr['milestone']}")
        print(f"Time Estimate: {mr['time_estimate']}h")
        print(f"Time Spent: {mr['total_time_spent']}h")
        print(f"Comments: {mr['comments']}")
        print("\n")

if __name__ == "__main__":
    main()