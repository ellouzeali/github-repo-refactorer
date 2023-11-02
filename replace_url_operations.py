import os
import re
import subprocess
import gitlab
from gitlab.exceptions import GitlabHttpError
import git
from git import Repo
from github import Github
from github.GithubException import GithubException
import xml.etree.ElementTree as ET
import shutil


# Define Custom Error exception class
class UpdatePomXmlError(Exception):
    def __init__(self, message):
        super().__init__(message)


def update_pom_xml_file(xml_file, target_namespace, scm_connection, scm_developer_connection, scm_url):
    scm_element_successfully_updated = False

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Define the XML namespace
        namespace = {'ns': target_namespace}

        # Find the 'scm' element
        scm_element = root.find(".//ns:scm", namespaces=namespace)

        if scm_element is not None:
            # Find and update the 'connection' element within 'scm'
            connection_element = scm_element.find(".//ns:connection", namespaces=namespace)
            if connection_element is not None:
                connection_element.text = scm_connection
                print("Updated Connection:", connection_element.text)

            # Find and update the 'developerConnection' element within 'scm'
            developer_connection_element = scm_element.find(".//ns:developerConnection", namespaces=namespace)
            if developer_connection_element is not None:
                developer_connection_element.text = scm_developer_connection
                print("Updated Developer Connection:", developer_connection_element.text)

            # Find and update the 'url' element within 'scm'
            url_element = scm_element.find(".//ns:url", namespaces=namespace)
            if url_element is not None:
                url_element.text = scm_url
                print("Updated URL:", url_element.text)

            # Save the changes back to the XML file with the original namespaces
            tree.write(xml_file, encoding='utf-8', xml_declaration=True, default_namespace=namespace['ns'])
            scm_element_successfully_updated = True
        else:
            raise UpdatePomXmlError("No 'scm' element found in the pom.xml file.")

    except ET.ParseError as e:
        raise UpdatePomXmlError(f"Error parsing XML: {str(e)}")
    except FileNotFoundError as e:
        raise UpdatePomXmlError(f"File not found: {str(e)}")
    except Exception as e:
        raise UpdatePomXmlError(f"An error occurred in update_scm_elements: {str(e)}")
    
    return scm_element_successfully_updated



def update_scm_connections_in_maven_repositories(github_project_url, github_access_token, github_project_path_segment):
    print(" Edit pom.xml files")
    had_error = False
    error_message = ""
    tmp_dir = os.path.join(os.getcwd(), "temp_dir")

    try:
        # Create a directory to clone the repository into
        repo_name = github_project_url.split("/")[-1].replace(".git", "")
        repo_dir = os.path.join(tmp_dir, repo_name)

        # Create a Pre-signed repository Url
        github_signed_url = github_project_url.replace("https://", f"https://{github_access_token}@")

        print(f" Clone repo: {repo_name}")
        # Clone the private repository with the access token embedded in the URL
        git.Repo.clone_from(github_signed_url, repo_dir)

        # Initialize a Git repository object
        git_repo = git.Repo(repo_dir)

        # Fetch all remote branches
        git_repo.remotes.origin.fetch()

        # Prepare new SCM connections
        filename = "pom.xml"
        target_xml_namespace = "http://maven.apache.org/POM/4.0.0"
        scm_connection = f"scm:git:git@github.com:{github_project_path_segment}.git"    
        scm_developer_connection = f"scm:git:git@github.com:{github_project_path_segment}.git"
        scm_url = f"https://github.com/{github_project_path_segment}"

        # Iterate through all remote branches
        for remote_ref in git_repo.remotes.origin.refs:
            if remote_ref.remote_head:
                branch_name = remote_ref.remote_head
                if branch_name != "HEAD":
                    print(f"Checking out branch: {branch_name}")
                    git_repo.git.checkout(branch_name)

                    # Check if 'pom.xml' file exists
                    pom_xml_path = os.path.join(repo_dir, filename)
                    if os.path.exists(pom_xml_path):
                        pom_successfully_updated = False
                        try:
                            pom_successfully_updated = update_pom_xml_file(pom_xml_path, target_xml_namespace, scm_connection, scm_developer_connection, scm_url)
                        except UpdatePomXmlError as e:
                            print(f"An error occurred in update_pom_xml_file: {str(e)}")
                            had_error = True
                            error_message = error_message + f"===> An error occurred in update_pom_xml_file on branch: {branch_name}, error message: {str(e)} \n"

                        if pom_successfully_updated:
                            print("SCM connections were successfully updated in the pom file")

                            # Commit the changes
                            git_repo.index.add(['pom.xml'])
                            git_repo.index.commit(f"Update 'pom.xml' for branch: {branch_name}")

                            # Push the changes to GitHub
                            git_repo.remotes.origin.push(branch_name)
                            print(f"Pushed changes for branch: {branch_name} to GitHub")
                        else:
                            print("An issue occurred during updating SCM connections in the pom file")
                            had_error = True
                            error_message = error_message + f"===> An issue occurred during updating SCM connections in the pom.xml file on branch: {branch_name} \n"
            
        # Remove the cloned project from the local filesystem
        print(f" Cleaning repo directory: {repo_dir}")
        shutil.rmtree(repo_dir)

    except git.exc.GitError as e:
        print(f"***edit_pom_xml*** Git error: {e}")
        had_error = True
        error_message = error_message + f"===> A Git error occured: {e} \n"
    except Exception as e:
        print(f"***edit_pom_xml*** An unexpected error occurred: {e}")
        had_error = True
        error_message = error_message + f"===> An unexpected error occurred: {e} \n"
    finally:
        # Clean up by deleting the temporary directory
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return had_error, error_message 





def edit_and_commit_github_file (github_repo_url, github_token, github_repo_branch_name, github_file_path, old_string, new_string):
    had_error = False
    error_message = ""
    try:
        # Extract the username and repository name from the GitHub URL
        repo_url_parts = github_repo_url.strip("/").split("/")
        username, repo_name = repo_url_parts[-2], repo_url_parts[-1]

        print (f"Github Project: {github_repo_url} , Branch: {github_repo_branch_name}")
        print (f"File Path: {github_file_path}")
        print (f"Changing Gitlab url: {old_string} with new Github url: {new_string}")

        # Create a Github instance and authenticate with your personal access token
        g = Github(github_token)

        # Get the specified repository
        repo = g.get_repo(f"{username}/{repo_name}")

        # Get the repo branch
        repo_branch = repo.get_branch(github_repo_branch_name)

        # Get the file content
        file = repo.get_contents(github_file_path, ref=repo_branch.name)

        # Read the content of the file
        file_content = file.decoded_content.decode("utf-8")

        # Check if old_string exists in file_content before replacing it
        if old_string in file_content:
            # Replace old_string with new_string in the file content
            updated_content = file_content.replace(old_string, new_string)

            # Retrive the new project name
            project_name = new_string.strip("/").split("/")[-1]
            
            # Update the file with the new content
            repo.update_file(
                path=github_file_path,
                message=f"Change Gitlab url to Github url for {project_name}",
                content=updated_content,
                sha=file.sha,
                branch=repo_branch.name
            )

            print("File updated and committed successfully!")
        else:
            had_error = True
            error_message = f"===>  Warning!! Gitlab URL: {old_string} was not found in {github_file_path}"            

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        had_error = True
        error_message = f"===> An error occurred: {str(e)}"
    finally:
        return had_error, error_message





if __name__ == "__main__":
    github_project_url = "https://github.com/yourusername/your_private_repo.git" 
    github_access_token = "<ACCESS_TOKEN>"  # Replace with your repository URL
    gitlab_project_path_segment = "old/gitlab/path"
    github_project_path_segment = "new/github/path"

    edit_pom_xml(github_project_url, github_access_token, gitlab_project_path_segment, github_project_path_segment)

    ############################################################################################################################
    github_repo_url = "https://github.com/yourusername/your-repo"
    github_token = "your_personal_access_token"
    github_repo_branch_name = "master"
    github_file_path = "group_vars/all/azure-devops.yml"
    old_string = "old_gitlab_url"
    new_string = "new_github_url"
    
    edit_and_commit_github_file(github_repo_url, github_token, github_repo_branch_name, github_file_path, old_string, new_string)


    ############################################################################################################################
    github_project_url = "https://github.com/yourusername/your_private_repo.git" 
    github_access_token = "<ACCESS_TOKEN>"  # Replace with your repository URL
    github_project_path_segment = "new/github/path"

    update_scm_connections_in_maven_repositories(github_project_url, github_access_token,  github_project_path_segment)