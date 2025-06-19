
# git_archiver

This repository includes utilities to make an archival copy of a Bitbucket workspace

The utilities use a Bitbucket [App Password](https://support.atlassian.com/bitbucket-cloud/docs/create-an-app-password/) and a github [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for API access, so you will need to generate an App Password to pass to the scripts.   Make sure to keep these credentials private; don't put it in the git repo!

## git_archive_clone.py

This program will query bitbucket and github via the API for a list off all repositories and then make two clones:

1. Mirror clone creates a bare clone of the repository that includes all refs and remote-tracking branches, and it also sets up the remote configuration so that git push --mirror will update everything in the destination repo to match the source.
2. Working copy clone is the default clone to provide a working snapshot of each repo.

See source code for usage and examples
