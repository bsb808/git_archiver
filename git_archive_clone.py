import os
import requests
import argparse

'''
This script clones all repositories from a Bitbucket workspace.

It requires a Bitbucket username, an app password, and the workspace name.

Usage:
python git_archive_clone.py --username <your_username> --app-password <your_app_password> --workspace <your_workspace>
python git_archive_clone.py --username brian_bingham --app-password AT*************B --workspace GFOE

Make sure to create an app password in Bitbucket with the necessary permissions to read repositories, see https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/
'''
# Parse command line arguments
parser = argparse.ArgumentParser(description="Clone all repositories from a Bitbucket workspace.")
parser.add_argument("--username", required=True, help="Bitbucket username")
parser.add_argument("--app-password", required=True, help="Bitbucket app password for the user, see https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/")
parser.add_argument("--workspace", required=True, default="GFOE", help="Bitbucket workspace name (default: GFOE)")
args = parser.parse_args()

USERNAME = args.username
APP_PASSWORD = args.app_password
WORKSPACE = args.workspace


# URL to fetch the first page of repositories
# This URL includes the `pagelen` parameter to limit the number of results per page
next_page_url = f"https://api.bitbucket.org/2.0/repositories/{WORKSPACE}?pagelen=100&fields=next,values.slug"

# Keep fetching pages while there's a page to fetch
full_repo_list = []
while next_page_url is not None:
    response = requests.get(next_page_url, auth=(USERNAME, APP_PASSWORD))
    page_json = response.json()

    # Parse repositories from the JSON
    for repo in page_json['values']:
        full_repo_list.append(repo['slug'])

    # Get the next page URL, if present
    # It will include same query parameters, so no need to append them again
    next_page_url = page_json.get('next', None)

# Result length will be equal to `size` returned on any page
print ("Result:", len(full_repo_list))

# Crete two directories, one for a mirror and one for a working copy
MIRROR_DIR = os.path.join(os.getcwd(), WORKSPACE, "mirror")
WORKING_DIR = os.path.join(os.getcwd(), WORKSPACE, "working_copy")

for dir_path in [MIRROR_DIR, WORKING_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# For each repository, clone it
N = len(full_repo_list)
print(f"Cloning {N} repositories...")
for repo, ii in zip(full_repo_list, range(1, N + 1)):
    repo_url = f"git@bitbucket.org:{WORKSPACE}/{repo}.git"
    
    # Mirror clone the repository
    os.chdir(MIRROR_DIR)
    print(f"Mirroring repository {ii}/{N}: {repo}")
    os.system(f"git clone --mirror {repo_url}")  
    
    # Clone the repository to a working copy
    os.chdir(WORKING_DIR)
    print(f"Cloning repository {ii}/{N}: {repo}")
    os.system(f"git clone {repo_url}")
    os.chdir(os.path.join(WORKING_DIR, repo))
    # Pull all the branches
    os.system("git pull --all")

# Print the completion message
print("All repositories have been cloned successfully.")





