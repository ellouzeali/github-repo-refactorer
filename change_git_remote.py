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
    print(f"**** Checking {directory} Folder ****")
    repo_path = os.path.join(os.getcwd(), directory)
    
    # Check if it's a Git repository
    try:
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        print(f"{directory} is not a Git repository")
        continue
    
    print(f"{directory} is a Git repository")
    origin_url = repo.remotes.origin.url

    print(f"Checking Origin Remote")
    # Check if the origin remote exists in the mapping
    if origin_url in remote_mapping:
        print(f"Origin Remote: {origin_url} has a matching remote in the mapping.")
        new_remote_url = remote_mapping[origin_url]
        
        # Change the remote URL to SSH format
        if new_remote_url.startswith("https://github.com"):
            new_remote_url = new_remote_url.replace("https://github.com/", "git@github.com:")
            if not new_remote_url.endswith(".git"):
                new_remote_url += ".git"
        
        print(f"Updating repository in {directory} from {origin_url} to {new_remote_url}")

        # Set the new remote URL
        subprocess.run(["git", "remote", "set-url", "origin", new_remote_url], cwd=repo_path, stdout=subprocess.PIPE)
        print(f"Repository in {directory} updated successfully.")
    else:
        print(f"Repository in {directory} has no matching remote in the mapping.")

print("Finished updating repositories.")
