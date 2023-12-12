import csv
from urllib.parse import urlparse

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
    # Parse the URL
    parsed_url = urlparse(repo_url)

    # Extract the path and remove leading/trailing slashes
    path_parts = parsed_url.path.strip('/').split('/')

    # Check if the URL is from GitHub or GitLab
    if 'github' in parsed_url.netloc:
        # GitHub URL structure: /<organization>/<repository>.git
        return '/'.join(path_parts[1:-1])
    elif 'gitlab' in parsed_url.netloc:
        # GitLab URL structure: /<group>/<subgroup>/.../<repository>.git
        return '/'.join(path_parts[1:-1])
    else:
        # Unsupported repository host
        raise ValueError(f"Unsupported repository host in URL: {repo_url}")
    


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