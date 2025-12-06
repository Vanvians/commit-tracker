"""
tracker.py

Utilities to analyze a local Git repository and produce two outputs:
 - output_1.txt: per-commit lists of added/deleted/modified files
 - output_2.csv: per-file metrics (commit count, average churn, unique contributors)
"""
import subprocess
import re
import csv


def run_git_commands(repo_path, commands):
    """
    Run a git command in the given repository and return stdout as a stripped string.
    """
    result = subprocess.run(
        ["git"] + commands,
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip()


def collect_commit_hashes(repo_path):
    """
    Collects all commit hashes in chronological order (oldest first).
    """
    commits = run_git_commands(repo_path, ["log", "--pretty=format:%H", "--reverse"])
    return commits.split("\n") if commits else []


def list_files_in_commit(repo_path, commit_hash):
    """
    List files present in a specific commit.
    """
    files = run_git_commands(repo_path, ["ls-tree", "-r", "--name-only", commit_hash])
    return files.split("\n") if files else []


def find_file_changes(repo_path, old, new):
    """
    Determine file-level changes between two commits.
    """
    changes = run_git_commands(repo_path, ["diff", "--name-status", old, new])
    change_list = []
    for line in changes.split("\n"):
        if line.strip():
            parts = line.split("\t")
            if len(parts) >= 2:
                status = parts[0]
                path = parts[1]
                change_list.append((status, path))
    return change_list


def get_file_commit_history(repo_path, file_path):
    """
    Get the commit history for a specific file.
    """
    commits = run_git_commands(repo_path, ["log", "--pretty=format:%H", "--", file_path])
    return commits.split("\n") if commits else []


def compute_churn(repo_path, commit_hash, file_path):
    """
    Compute churn (added + deleted lines) for a single file at a given commit.
    """
    result = run_git_commands(repo_path, ["show", "--numstat", commit_hash, "--" , file_path])

    for line in result.split("\n"):
        parts = line.split("\t")
        if len(parts) == 3 and parts[2] == file_path:
            added, deleted = parts[0], parts[1]
            if added.isdigit() and deleted.isdigit():
                return int(added) + int(deleted)
    return 0
            

def count_unique_contributors(repo_path, commit_hash, file_path):
    """
    Count unique contributors to a file using git blame output.
    """
    result = run_git_commands(repo_path, ["blame", commit_hash, "--", file_path])

    contributors = set()

    # The regex attempts to capture the author name in blame lines like:
    #   ^<sha> (<Author Name> YYYY-MM-DD ...) <line>
    # It matches up to the first date-like token.
    pattern = r"\(([^()]+?)\s+\d{4}-"

    for line in result.split("\n"):
        match = re.search(pattern, line)
        if match:
            name = match.group(1).strip()
            contributors.add(name)

    return len(contributors)


def output_1(repo_path):
    """
    Generate output_1.txt containing per-commit file changes.
    """
    commits = collect_commit_hashes(repo_path)

    with open("output_1.txt", "w") as f:
        for i in range(1, len(commits)):
            old_commit = commits[i - 1]
            new_commit = commits[i]

            changes = find_file_changes(repo_path, old_commit, new_commit)

            added = [p for s, p in changes if s == "A"]
            deleted = [p for s, p in changes if s == "D"]
            modified = [p for s, p in changes if s == "M"]

            if added:
                f.write(f"Commit #: {new_commit} Added files:\n")
                for file in added:
                    f.write(f"  {file}\n")
            if deleted:
                f.write(f"Commit #: {new_commit} Deleted files:\n")
                for file in deleted:
                    f.write(f"  {file}\n")
            if modified:
                f.write(f"Commit #: {new_commit} Modified files:\n")
                for file in modified:
                    f.write(f"  {file}\n")
            
            f.write("\n")
    print("output_1.txt generated successfully.")


def output_2(repo_path):
    """
    Generate output_2.csv containing per-file metrics.

    Columns: File name, File path, Commit count, Average Churn, Unique contributors
    """
    last_commit = run_git_commands(repo_path, ["rev-parse", "master"])

    files = list_files_in_commit(repo_path, last_commit)

    # Collect all data first
    data = []
    for file_path in files:
        commit_count_list = get_file_commit_history(repo_path, file_path)
        commit_count = len(commit_count_list)

        churn_values = []
        contributor_number = []

        for commit in commit_count_list:
            churn_values.append(
                compute_churn(repo_path, commit, file_path)
            )
            contributor_number.append(
                count_unique_contributors(repo_path, commit, file_path)
            )

        average_churn = sum(churn_values) / len(churn_values) if churn_values else 0
        avg_contributors = sum(contributor_number) / len(contributor_number) if contributor_number else 0

        data.append([file_path.split("/")[-1], file_path, str(commit_count), f"{average_churn:.2f}", f"{avg_contributors:.2f}"])

    # Calculate column widths
    headers = ["File name", "File path", "Commit count", "Average Churn", "Unique contributors"]
    col_widths = [max(len(str(headers[i])), max(len(row[i]) for row in data)) if data else len(headers[i]) for i in range(5)]

    with open("output_2.csv", "w", newline = "") as f: 
        writer = csv.writer(f)
        # Write padded header
        padded_header = [headers[i].ljust(col_widths[i]) for i in range(5)]
        writer.writerow(padded_header)

        # Write padded data
        for row in data:
            padded_row = [row[i].ljust(col_widths[i]) for i in range(5)]
            writer.writerow(padded_row)

    print("output_2.csv generated successfully.")


#Main
if __name__ == "__main__":
    """
    Entry point: request a repository path from the user and generate both outputs.
    """
    repo_path = input(" Please enter the path to your Git repository here:").strip()

    output_1(repo_path)
    output_2(repo_path)

    print("Analysis complete. Results saved to output_1.txt and output_2.csv")
