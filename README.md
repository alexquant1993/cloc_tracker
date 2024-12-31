# GitHub Commit Analyzer

This Python script is designed to analyze and report on commit activity in GitHub repositories, focusing on specific users and branches. It fetches commit data using the GitHub API and processes it to provide insights into the contributions of individual team members.

## Features

- Fetch commit data from specified GitHub branches and users.
- Analyze commit details including lines added, lines removed, and effective lines of code (ELOC).
- Export commit data to an Excel file with separate sheets for each user.
- Update the Excel file with new commits while avoiding duplicate entries.
- Configure settings through a JSON file for enhanced flexibility and security.

## Configuration

Modify the `config.json` file to set up your repository details, GitHub token, local repository path, target users, and folder path. Ensure not to track `config.json` in version control to keep sensitive information secure.

Example `config.json` structure:

```json
{
    "GITHUB_REPO": "user/repo",
    "GITHUB_TOKEN": "your_github_token",
    "LOCAL_REPO_PATH": "path_to_local_repo",
    "USERS": [
        "username1",
        "username2"
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

## Installation

1. Install Poetry if it is not already installed:
   ```bash
   pip install poetry
   ```

2. Clone this repository and navigate to its directory:
   ```bash
   git clone https://github.com/alexquant1993/cloc-tracker.git
   cd cloc-tracker
   ```

3. Install the dependencies:
   ```bash
   poetry install
   ```

## Usage

1. Activate the Poetry environment:
   ```bash
   poetry shell
   ```

2. Run the script:
   ```bash
   python main.py
   ```

Ensure that `config.json` is properly configured before running the script.

## Output

The script generates an Excel file (`output_file_name.xlsx`) containing commit data. Each sheet corresponds to a user and includes the following columns:

- **COMMIT**: Commit hash.
- **AUTHOR**: Commit author.
- **LINES_ADDED**: Number of lines added.
- **LINES_REMOVED**: Number of lines removed.
- **ELOC**: Effective lines of code (added - removed).
- **COMMIT_URL**: URL to the commit on GitHub.
- **MESSAGE**: Commit message.
- **DATE**: Commit date.

## Functionality Breakdown

1. **Fetching Commits**: The script uses the GitHub API to fetch commits for specified users from the given repository.
2. **Commit Analysis**: For each commit, it calculates lines added, removed, and effective lines (added - removed).
3. **File Filtering**: Filters out files based on configurable paths, suffixes, and patterns.
4. **Excel Export**: Outputs processed data into an Excel file, updating existing data without duplications.

## Key Functions

- `fetch_all_commits(repo_name, author)`: Fetches all commits for a given author in the repository.
- `should_include_file(file_path)`: Determines if a file should be included based on the specified folder paths, suffixes, and patterns.
- `get_commit_stats(repo, commit_hash)`: Computes stats for a specific commit, including lines added and removed.
- `main()`: Coordinates the script's execution flow, including data processing and Excel file updates.

## Notes

- The script assumes the local repository is already cloned and up-to-date.
- Ensure your GitHub token has sufficient permissions to access the repository.
- The script checks out to the main branch upon completion to avoid leaving the repository in a detached state.

---

This documentation is designed to help you understand and use the script effectively. Feel free to modify it based on your specific use case.