import getpass
from github import Github

def get_github_username(github_token, full_name):
    g = Github(github_token)
    users = g.search_users(full_name + " in:fullname")
    for user in users:
        return user.login
    return None


# Example usage
def main():


    github_token = getpass.getpass("Enter your GITHUB_TOKEN: ")

    users = ["Nassim Kebbani", "Thibault Deregnaucourt", "Ali ELLOUZE", "Julie Franel", "Olivier Lemaire"]

    for user in users:
        print("****************************************")
        print(f"User: {user}")
        username = get_github_username(github_token, user)
        print(f"Username: {username}")


if __name__ == "__main__":
    main()