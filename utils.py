import csv
import re

def get_project_list (file_path):
    project_list = []

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')

        for line_number, row in enumerate(reader, start=2):  # Start at line 2 to account for header
            old_gitlab_repo_url = row.get('Old_Gitlab_URL')
            github_repo_url = row.get('Github_URL')

            if not old_gitlab_repo_url or not github_repo_url:
                raise ValueError(f"Missing data on line {line_number}.")

            project = {
                "old_gitlab_repo_url": old_gitlab_repo_url,
                "github_repo_url": github_repo_url,
            }
            
            project_list.append(project)

    if not project_list:
        raise ValueError("No valid projects found in the file.")

    return project_list


def extract_repository_path(repo_url):
    # Define patterns to match the repository path
    github_pattern = re.compile(r'https://github\.com/(.*?)(\.git)?$', re.IGNORECASE)
    gitlab_pattern = re.compile(r'https://gitlab\.com/(.*?)(\.git)?$', re.IGNORECASE)

    # Check if the URL is a GitHub or GitLab URL
    match_github = github_pattern.match(repo_url)
    match_gitlab = gitlab_pattern.match(repo_url)

    if match_github:
        return match_github.group(1)
    elif match_gitlab:
        return match_gitlab.group(1)
    else:
        raise ValueError("Invalid repository URL")
    


# Example usage
def main():
    try:
        data_file_path = 'project-list.txt'
        projects = get_project_list(data_file_path)
        for project in projects:
            print(project)
    except ValueError as e:
        print("Error:", e)

if __name__ == "__main__":
    main()