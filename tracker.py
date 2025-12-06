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
            status = parts[0]
            path = parts[1]
            changes.append((status, path))
    return change_list

#Get list of all commits that modified a single file

def get_file_commit_history(repo_path, file_path):
    commits = run_git_commands(repo_path, ["log", "--pretty=format:%H", "--", file_path])
    return commits.split("\n") if commits else []

#Compute churn 

#Count unuique contributors to a file

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
                f.write(f"Commit #: {new_commit} Addes files:\n")
            if deleted:
                f.write(f"Commit #: {new_commit} Deleted files:\n")
            if modified:
                f.write(f"Commit #: {new_commit} Modified files:\n")
            
            f.write("\n")
    print("output_1.txt generated successfully.")

#Generate output_2.csv

#Main
if __name__ == "__main__":
    repo_path = input(" Please enter the path to your Git repository here:").strip()

    output_1(repo_path)
    output_2(repo_path)

    print("Analysis complete. Results saved to output_1.txt and output_2.csv")
