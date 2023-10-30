import csv

def get_project_list (file_path):
    project_list = []

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')

        for line_number, row in enumerate(reader, start=2):  # Start at line 2 to account for header
            old_gitlab_url = row.get('Old_Gitlab_URL')
            github_url = row.get('Github_URL')
            new_repo_name = row.get('New_Repo_Name')

            if not old_gitlab_url or not github_url or not new_repo_name:
                raise ValueError(f"Missing data on line {line_number}.")

            project = {
                "old_gitlab_url": old_gitlab_url,
                "github_url": github_url,
                "new_repo_name": new_repo_name
            }
            
            project_list.append(project)

    if not project_list:
        raise ValueError("No valid projects found in the file.")

    return project_list

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