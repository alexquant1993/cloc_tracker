import json
import logging
import os

import pandas as pd
import requests
from git import Repo
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load configuration file
with open("config.json") as config_file:
    config = json.load(config_file)

# Configuration variables
GITHUB_REPO = config["GITHUB_REPO"]
GITHUB_TOKEN = config["GITHUB_TOKEN"]
LOCAL_REPO_PATH = config["LOCAL_REPO_PATH"]
USERS = config["USERS"]
LIB_FOLDER_PATHS = config["LIB_FOLDER_PATHS"]
EXCLUDE_FILE_SUFFIXES = config["EXCLUDE_FILE_SUFFIXES"]
EXCLUDE_FILE_PATTERNS = config.get("EXCLUDE_FILE_PATTERNS", [])
EXCEL_FILE = config["EXCEL_FILE"]

# GitHub API Headers
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# Initialize Git Repo
repo = Repo(LOCAL_REPO_PATH)


def fetch_all_commits(repo_name, author):
    commits = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo_name}/commits?author={author}&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        logger.info(
            f"Fetching all commits for {author} (page {page}). Status code: {response.status_code}"
        )
        if response.status_code == 200:
            page_commits = response.json()
            if not page_commits:
                break
            commits.extend(page_commits)
            page += 1
        else:
            logger.warning(
                f"Failed to fetch commits. Status code: {response.status_code}"
            )
            break

    logger.info(f"Fetched a total of {len(commits)} commits for {author}")
    return commits


def should_include_file(file_path):
    if any(file_path.startswith(lib_path) for lib_path in LIB_FOLDER_PATHS):
        if not any(file_path.endswith(suffix) for suffix in EXCLUDE_FILE_SUFFIXES):
            if not any(pattern in file_path for pattern in EXCLUDE_FILE_PATTERNS):
                return True
    return False


def get_commit_stats(repo, commit_hash):
    repo.git.checkout(commit_hash, force=True)
    stats = repo.git.log(
        "-1", "--numstat", "--pretty=format:", commit_hash
    ).splitlines()
    logger.info(f"Raw stats for commit {commit_hash}: {stats}")

    added, removed = 0, 0
    for stat in stats:
        parts = stat.split()
        if len(parts) >= 3:
            a, r, file_path = parts[:3]
            if should_include_file(file_path):
                added += int(a)
                removed += int(r)

    logger.info(
        f"Processed stats for commit {commit_hash}: added={added}, removed={removed}"
    )
    return added, removed


def main():
    logger.info("Starting main function")

    # Load existing Excel file if it exists
    existing_data = {}
    if os.path.exists(EXCEL_FILE):
        logger.info(f"Loading existing data from {EXCEL_FILE}")
        with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl") as writer:
            for sheet_name in writer.sheets:
                existing_data[sheet_name] = pd.read_excel(
                    EXCEL_FILE, sheet_name=sheet_name
                )

    with pd.ExcelWriter(EXCEL_FILE, mode="w", engine="openpyxl") as writer:
        for user in tqdm(USERS, desc="Processing users"):
            logger.info(f"Processing user {user}")
            commits = fetch_all_commits(GITHUB_REPO, user)
            logger.info(f"Fetched {len(commits)} commits for {user}")
            new_data = []
            processed_commits = set()

            for commit in tqdm(commits, desc=f"Processing commits for {user}"):
                commit_hash = commit["sha"]
                if commit_hash in processed_commits:
                    continue
                processed_commits.add(commit_hash)

                commit_url = commit["html_url"]
                commit_message = commit["commit"]["message"]
                commit_date = commit["commit"]["author"]["date"]
                author = commit["commit"]["author"]["name"]
                lines_added, lines_removed = get_commit_stats(repo, commit_hash)
                effective_lines = lines_added - lines_removed

                new_data.append(
                    {
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

            logger.info(f"Processed {len(new_data)} unique commits for {user}")

            # Create a new DataFrame with the new data
            new_df = pd.DataFrame(new_data)
            sheet_name = f"{user}"

            if sheet_name in existing_data:
                logger.info(f"Combining existing and new data for {sheet_name}")
                # If user already exists in the data, combine the old and new data
                combined_df = (
                    pd.concat([existing_data[sheet_name], new_df])
                    .drop_duplicates(subset="COMMIT")
                    .reset_index(drop=True)
                )
            else:
                combined_df = new_df

            # Write the combined data to the Excel file
            logger.info(f"Writing data to Excel sheet {sheet_name}")
            combined_df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Checkout to the main branch
    repo.git.checkout("main")
    logger.info("Script execution completed")


if __name__ == "__main__":
    main()
