import os
import requests
import argparse
'''
This script clones all repositories from a Bitbucket workspace and github personal access token.

It requires a Bitbucket username, an app password, and the workspace name.

* Bitbucket app passwords can be created in your Bitbucket account settings: Settings > Personal settings > App passwords.
* GitHub personal access tokens can be created in your GitHub account settings: Settings > Developer settings > Personal access tokens.

Usage Example:
python git_archive_clone.py --username <your_username> --bitbucket-app-password <your_app_password> --github-token <your_github_token> --workspace <your_workspace>
python3 git_archive_clone.py --username brian_bingham --bitbucket-app-password ******************** --github-token ***************I --workspace GFOE

Make sure to create an app password in Bitbucket with the necessary permissions to read repositories, see https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/
'''
# Parse command line arguments
parser = argparse.ArgumentParser(description="Clone all repositories from a Bitbucket workspace.")
parser.add_argument("--username", required=True, help="Bitbucket username")
parser.add_argument("--bitbucket-app-password", required=True, help="Bitbucket app password for the user, see https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/")
parser.add_argument("--github-token", required=True, help="GitHub personal access token (if using GitHub)")
parser.add_argument("--workspace", required=True, default="GFOE", help="Bitbucket workspace name (default: GFOE)")
args = parser.parse_args()

USERNAME = args.username
APP_PASSWORD = args.bitbucket_app_password
GITHUB_TOKEN = args.github_token
WORKSPACE = args.workspace

def get_repositorylist(workspace, username, app_password, provider="bitbucket"):
    """
    Fetches the list of repositories from a Bitbucket or GitHub workspace/org.

    Args:
        workspace (str): The Bitbucket workspace or GitHub organization/user name.
        username (str): The Bitbucket/GitHub username.
        app_password (str): The Bitbucket app password or GitHub personal access token.
        provider (str): "bitbucket" or "github".

    Returns:
        list: A list of repository names/slugs in the workspace/org.
    """
    full_repo_list = []

    if provider.lower() == "bitbucket":
        url = f"https://api.bitbucket.org/2.0/repositories/{workspace}?pagelen=100&fields=next,values.slug"
        while url is not None:
            response = requests.get(url, auth=(username, app_password))
            response.raise_for_status()
            page_json = response.json()
            for repo in page_json.get('values', []):
                full_repo_list.append(repo['slug'])
            url = page_json.get('next', None)
    elif provider.lower() == "github":
        # GitHub paginates with 'per_page' and 'page'
        page = 1
        while True:
            url = f"https://api.github.com/orgs/{workspace}/repos?per_page=100&page={page}"
            headers = {"Authorization": f"token {app_password}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            repos = response.json()
            if not repos:
                break
            for repo in repos:
                full_repo_list.append(repo['name'])
            page += 1
    else:
        raise ValueError("Unsupported provider. Use 'bitbucket' or 'github'.")

    # If the list is empty, print a message and exit
    if not full_repo_list:
        print(f"No repositories found in workspace '{WORKSPACE}'.")
        return []
    else:
        # Print the total number of repositories found
        print(f"Total repositories found in {provider} workspace '{WORKSPACE}': {len(full_repo_list)}")
    
    return full_repo_list


def clone_repos(repo_list, workspace, provider="bitbucket"):
    """
    Clones the repositories from a given list into a specified directory.

    Args:
        repo_list (list): List of repository names/slugs to clone.
        workspace (str): The Bitbucket workspace or GitHub organization/user name.
        provider (str): "bitbucket" or "github".
    """
    # Create directories for mirror and working copy
    MIRROR_DIR = os.path.join(os.getcwd(), f"{workspace}_{provider}", "mirror")
    WORKING_DIR = os.path.join(os.getcwd(), f"{workspace}_{provider}", "working_copy")
    CURRENT_DIR = os.getcwd()

    for dir_path in [MIRROR_DIR, WORKING_DIR]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    N = len(repo_list)
    print(f"Cloning {N} repositories from {provider}...")

    for ii, repo in enumerate(repo_list, start=1):
        repo_url = f"git@{provider}.com:{workspace}/{repo}.git"
        
        # Mirror clone the repository
        os.chdir(MIRROR_DIR)
        print(f"Mirroring repository {ii}/{N}: {repo} from {repo_url}")
        os.system(f"git clone --mirror {repo_url}")

        # Clone the repository to a working copy
        os.chdir(WORKING_DIR)
        print(f"Cloning repository {ii}/{N}: {repo}")
        os.system(f"git clone {repo_url}")
        os.chdir(os.path.join(WORKING_DIR, repo))
        # Pull all the branches
        os.system("git pull --all")

    os.chdir(CURRENT_DIR)
    print(f"All repositories from {provider} have been cloned successfully.")

for provider in ["bitbucket", "github"]:
    print(f"Fetching repositories from {provider} workspace '{WORKSPACE}'...")
    if provider == "bitbucket":
        # Fetch the list of repositories from the Bitbucket workspace
        bb_repo_list = get_repositorylist(WORKSPACE, USERNAME, APP_PASSWORD)
        clone_repos(bb_repo_list, WORKSPACE, provider="bitbucket")
    else:
        # Fetch the list of repositories from the github workspace
        gh_repo_list = get_repositorylist(WORKSPACE, USERNAME, GITHUB_TOKEN, provider="github")
        clone_repos(gh_repo_list, WORKSPACE, provider="github")