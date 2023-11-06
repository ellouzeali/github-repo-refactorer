import os
import git
import subprocess

# Read the remote mapping from remote-list.txt
remote_mapping = {}
with open("remote-list.txt", "r") as remote_file:
    for line in remote_file:
        gitlab_remote, github_remote = line.strip().split('\t')
        remote_mapping[gitlab_remote] = github_remote

# Get the list of directories in the current context
directories = [d for d in os.listdir() if os.path.isdir(d)]

# Iterate through the directories and update Git repositories
for directory in directories:
    repo_path = os.path.join(os.getcwd(), directory)
    
    # Check if it's a Git repository
    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        continue
    
    origin_url = repo.remotes.origin.url

    # Check if the origin remote exists in the mapping
    if origin_url in remote_mapping:
        new_remote_url = remote_mapping[origin_url]
        print(f"Updating repository in {directory} from {origin_url} to {new_remote_url}")
        
        # Change the remote URL
        subprocess.run(["git", "remote", "set-url", "origin", new_remote_url], cwd=repo_path, stdout=subprocess.PIPE)
        print(f"Repository in {directory} updated successfully.")
    else:
        print(f"Repository in {directory} has no matching remote in the mapping.")

print("Finished updating repositories.")