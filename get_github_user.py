import getpass
from github import Github

def get_github_username(github_token, full_name, organization_name):
    g = Github(github_token)
    query = full_name + " in:fullname type:user org:" + organization_name
    users = g.search_users(query)
    for user in users:
        return user.login
    return None



def get_username_by_full_name(github_token, member_full_name, organization_name):
    # Authenticate to GitHub
    g = Github(github_token)
    
    # Get the organization
    org = g.get_organization(organization_name)
    
    # Get the members of the organization
    members = org.get_members()

    print(f"################ Memebers: {}members")
    
    # Search for the member by full name and return their username
    for member in members:
        if member.name == member_full_name:
            return member.login
    
    return None  # Return None if the member is not found

# Example usage
def main():


    github_token = getpass.getpass("Enter your GITHUB_TOKEN: ")

    users = ["Nassim Kebbani", "Thibault Deregnaucourt", "Ali ELLOUZE", "Julie Franel", "Olivier Lemaire"]
    organization_name = "TotalEnergiesCode"

    for user in users:
        print("****************************************")
        print(f"User: {user}")
        username = get_username_by_full_name(github_token, user, organization_name)
        print(f"Username: {username}")






if __name__ == "__main__":
    main()