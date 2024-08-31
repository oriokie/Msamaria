#!/bin/bash
OLD_EMAIL="“oriokie@icloud.com”"
CORRECT_NAME="Edwin K. Orioki"
CORRECT_EMAIL="oriokie@icloud.com"

for REPO in /path/to/repos/*; do
  if [ -d "$REPO/.git" ]; then
    cd "$REPO"
    git filter-repo --commit-callback '
    if commit.author_email == b"$OLD_EMAIL":
        commit.author_name = b"$CORRECT_NAME"
        commit.author_email = b"$CORRECT_EMAIL"
    if commit.committer_email == b"$OLD_EMAIL":
        commit.committer_name = b"$CORRECT_NAME"
        commit.committer_email = b"$CORRECT_EMAIL"
    '
    git push --force --tags origin 'refs/heads/*'
  fi
done

