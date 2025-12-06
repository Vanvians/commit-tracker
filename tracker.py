import subprocess
import re
import csv


#Run Git

def run_git_commands(repo_path, commands):
    result = subprocess.run(
        ["git"] + commands,
        cwd = repo_path,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True
    )
    return result.stdout.strip()

#collect commit hashes

def collect_commit_hashes(repo_path):
    commits = run_git_commands(repo_path, ["log", "--pretty=format:%H", "--reverse"])
    return commits.split("\n") if commits else []

#List all files in a commit

def list_files_in_commit(repo_path, commit_hash):
    files = run_git_commands(repo_path, ["ls-tree", "--name-only", "r", commit_hash])
    return files.split("\n") if files else []

#Find added/deleted/modified files

def find_file_changes(repo_path, old, new):
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

#Get list of all commits that modified a single file

def get_file_commit_history(repo_path, file_path):
    commits = run_git_commands(repo_path, ["log", "--pretty=format:%H", "--", file_path])
    return commits.split("\n") if commits else []

#Compute churn 

def compute_churn(repo_path, commit_hash, file_path):
    result = run_git_commands(repo_path, ["show", "--numstat", commit_hash, "--" , file_path])

    for line in result.split("\n"):
        parts = line.split("\t")
        if len(parts) == 3 and parts[2] == file_path:
            added, deleted = parts[0], parts[1]
            if added.isdigit() and deleted.isdigit():
                return int(added) + int(deleted)
    return 0
            

#Count unique contributors to a file

def count_unique_contributors(repo_path, commit_hash,file_path):
    result = run_git_commands(repo_path, ["blame", commit_hash, "--", file_path])

    contributors = set()

    pattern = r"\(([^()]+?)\s+\d{4}-"

    for line in result.split("\n"):
        match = re.match(pattern, line)
        if match:
            name = match.group(1).strip()
            contributors.add(name)

    return len(contributors)


#Generate output_1.txt

def output_1(repo_path):
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
            if deleted:
                f.write(f"Commit #: {new_commit} Deleted files:\n")
            if modified:
                f.write(f"Commit #: {new_commit} Modified files:\n")
            
            f.write("\n")
    print("output_1.txt generated successfully.")

#Generate output_2.csv

def output_2(repo_path):
    last_commit = run_git_commands(repo_path, ["rev-parse", "master"])

    files = list_files_in_commit(repo_path, last_commit)

    with open("output_2.csv", "w", newline = "") as f: 
        writer = csv.writer(f)
        writer.writerow(["File name", "File path", " Commit count", "Average Churn", "Unique contributors"])

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
                    count_unique_contributors(repo_path, file_path)
                )

            average_churn = sum(churn_values) / len(churn_values) if churn_values else 0
            avg_contributors = sum(contributor_number) / len(contributor_number) if contributor_number else 0

            writer.writerow([file_path.split("|")[-1], file_path, commit_count, f"{average_churn:.2f}", f"{avg_contributors:.2f}"])
    print("output_2.csv generated successfully.")


#Main
if __name__ == "__main__":
    repo_path = input(" Please enter the path to your Git repository here:").strip()

    output_1(repo_path)
    output_2(repo_path)

    print("Analysis complete. Results saved to output_1.txt and output_2.csv")
