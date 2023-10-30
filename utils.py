import csv

def exctract_data_from_file(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        
        for row in reader:
            old_gitlab_url = row['Old_Gitlab_URL']
            github_url = row['Github_URL']
            new_repo_name = row['New_Repo_Name']
            
            print("Old Gitlab URL:", old_gitlab_url)
            print("Github URL:", github_url)
            print("New Repo Name:", new_repo_name)
            print()

# Example usage
def main():
    data_file_path = 'project-list.txt'
    exctract_data_from_file(data_file_path)

if __name__ == "__main__":
    main()