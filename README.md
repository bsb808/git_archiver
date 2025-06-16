
# git_archiver

This repository includes utilities to make an archival copy of a Bitbucket workspace

The utilities us a Bitbucket [App Password](https://support.atlassian.com/bitbucket-cloud/docs/create-an-app-password/) for API access, so you will need to generate an App Password to pass to the scripts

## git_archive_clone.py

This program will query bitbucket via the API for a list off all repositories and then make two clones:

1. Mirror clone creates a bare clone of the repository that includes all refs and remote-tracking branches, and it also sets up the remote configuration so that git push --mirror will update everything in the destination repo to match the source.
2. Working copy clone is the default clone to provide a working snapshot of each repo


## Usage

```
python git_archive_clone.py --username <your_username> --app-password <your_app_password> --workspace <your_workspace>
```

```
python git_archive_clone.py --username brian_bingham --app-password AT*************B --workspace GFOE
```