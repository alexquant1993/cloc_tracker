# GitHub Commit Analyzer

This Python script is designed to analyze and report on commit activity in GitHub repositories, focusing on specific users and branches. It fetches commit data using the GitHub API and processes it to provide insights into the contributions of individual team members.

## Features

- Fetch commit data from specified GitHub branches and users.
- Analyze commit details including lines added, lines removed, and effective lines of code (ELOC).
- Export commit data to an Excel file with separate sheets for each user-branch combination.
- Update the Excel file with new commits while avoiding duplicate entries.
- Configure settings through a JSON file for enhanced flexibility and security.

## Configuration

Modify the `config.json` file to set up your repository details, GitHub token, local repository path, target users, branches, and folder path. Ensure not to track `config.json` in version control to keep sensitive information secure.

Example `config.json` structure:

```json
{
    "GITHUB_REPO": "user/repo",
    "GITHUB_TOKEN": "your_github_token",
    "LOCAL_REPO_PATH": "path_to_local_repo",
    "USERS_BRANCHES": [
        {"USER": "username1", "BRANCH": "branch1"},
        {"USER": "username2", "BRANCH": "branch2"}
    ],
    "LIB_FOLDER_PATHS": [
        "folder/path1/",
        "folder/path2/"
    ],
    "EXCLUDE_FILE_SUFFIXES": [
        ".g.dart"
    ],
    "EXCLUDE_FILE_PATTERNS": [
        "test/",
        "docs/",
        "README"
    ],
    "EXCEL_FILE": "output_file_name.xlsx"
}
```