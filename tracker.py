import subprocess


#Main
if __name__ == "__main__":
    repo_path = input(" Please enter the path to your Git repository here:").strip()

    output_1(repo_path)
    output_2(repo_path)

    print("Analysis complete. Results saved to output_1.txt and output_2.csv")


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
    return commits.split("\n") if output else []

#List all files in a commit

#Find added/deleted/modified files

#Get list of all commits that modified a single file

#Compute churn 

#Count unuique contributors to a file

#Generate output_1.txt

#Generate output_2.csv