import json
import os

import pandas as pd
import requests
from git import Repo
from tqdm import tqdm

# Load configuration file
with open("config.json") as config_file:
    config = json.load(config_file)

# Configuration variables
GITHUB_REPO = config["GITHUB_REPO"]
GITHUB_TOKEN = config["GITHUB_TOKEN"]
LOCAL_REPO_PATH = config["LOCAL_REPO_PATH"]
USERS_BRANCHES = [(user["USER"], user["BRANCH"]) for user in config["USERS_BRANCHES"]]
LIB_FOLDER_PATH = config["LIB_FOLDER_PATH"]
EXCEL_FILE = config["EXCEL_FILE"]

# GitHub API Headers
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# Initialize Git Repo
repo = Repo(LOCAL_REPO_PATH)


def fetch_commits(repo_name, branch, author):
    # Fetch commits from a GitHub repository
    url = f"https://api.github.com/repos/{repo_name}/commits?q=sha={branch}&author={author}&per_page=100"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []


def get_commit_stats(repo, commit_hash):
    # Get commit stats for a specific commit
    repo.git.checkout(commit_hash, force=True)
    stats = repo.git.log(
        "-1", "--numstat", "--pretty=format:", commit_hash
    ).splitlines()

    added, removed = 0, 0
    for stat in stats:
        a, r, file_path = stat.split()[:3]

        if file_path.startswith(LIB_FOLDER_PATH):
            added += int(a)
            removed += int(r)

    return added, removed


def main():
    # Load existing Excel file if it exists
    existing_data = {}
    if os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl") as writer:
            for sheet_name in writer.sheets:
                existing_data[sheet_name] = pd.read_excel(
                    EXCEL_FILE, sheet_name=sheet_name
                )

    with pd.ExcelWriter(EXCEL_FILE, mode="w", engine="openpyxl") as writer:
        for user, branch in tqdm(USERS_BRANCHES, desc="Processing users"):
            commits = fetch_commits(GITHUB_REPO, branch, user)
            new_data = []

            for commit in tqdm(commits, desc=f"Processing commits for {user}/{branch}"):
                commit_hash = commit["sha"]
                commit_url = commit["html_url"]
                commit_message = commit["commit"]["message"]
                commit_date = commit["commit"]["author"]["date"]
                author = commit["commit"]["author"]["name"]
                lines_added, lines_removed = get_commit_stats(repo, commit_hash)
                effective_lines = lines_added - lines_removed

                new_data.append(
                    {
                        "BRANCH": branch,
                        "COMMIT": commit_hash,
                        "AUTHOR": author,
                        "LINES_ADDED": lines_added,
                        "LINES_REMOVED": lines_removed,
                        "ELOC": effective_lines,
                        "COMMIT_URL": commit_url,
                        "MESSAGE": commit_message,
                        "DATE": commit_date,
                    }
                )

            # Create a new DataFrame with the new data
            new_df = pd.DataFrame(new_data)
            sheet_name = f"{user}_{branch}"

            if sheet_name in existing_data:
                # If user already exists in the data, combine the old and new data
                combined_df = (
                    pd.concat([existing_data[sheet_name], new_df])
                    .drop_duplicates(subset="COMMIT")
                    .reset_index(drop=True)
                )
            else:
                combined_df = new_df

            # Write the combined data to the Excel file
            combined_df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Checkout to the main branch
    repo.git.checkout("main")


if __name__ == "__main__":
    main()
