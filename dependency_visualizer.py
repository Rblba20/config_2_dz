import argparse
import os
import subprocess
import tempfile
from datetime import datetime
from git import Repo

def clone_repo(repo_url):
    temp_dir = tempfile.mkdtemp()
    print(f"Cloning repository {repo_url} into {temp_dir}")
    Repo.clone_from(repo_url, temp_dir)
    return temp_dir

def get_commit_dependencies(repo_path, since_date):
    repo = Repo(repo_path)
    if not repo.bare:
        commits = repo.iter_commits(since=since_date)
        dependencies = []
        for commit in commits:
            files = [item.a_path for item in commit.stats.files]
            dependencies.append({
                "hash": commit.hexsha[:7],
                "files": files,
                "parents": [parent.hexsha[:7] for parent in commit.parents]
            })
        return dependencies
    else:
        raise ValueError("Invalid repository path.")

def generate_mermaid_graph(dependencies):
    graph_lines = ["graph TD"]
    for dep in dependencies:
        node = f"{dep['hash']}[\"{', '.join(dep['files'])}\"]"
        graph_lines.append(node)
        for parent in dep["parents"]:
            graph_lines.append(f"{parent} --> {dep['hash']}")
    return "\n".join(graph_lines)

def save_mermaid_graph(mermaid_code, output_file, mmdc_path):
    mmd_file = output_file.replace(".png", ".mmd")
    with open(mmd_file, "w") as file:
        file.write(mermaid_code)

    subprocess.run([mmdc_path, "-i", mmd_file, "-o", output_file], check=True)
    os.remove(mmd_file)

def main():
    parser = argparse.ArgumentParser(description="Git dependency visualizer")
    parser.add_argument("--mmdc-path", required=True, help="Path to mmdc (Mermaid CLI).")
    parser.add_argument("--repo-path", required=True, help="Path to the git repository or URL.")
    parser.add_argument("--output-file", required=True, help="Path to the output PNG file.")
    parser.add_argument("--since-date", required=True, help="Start date for commits (YYYY-MM-DD).")

    args = parser.parse_args()
    since_date = datetime.strptime(args.since_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    # Clone repo if URL is provided
    repo_path = args.repo_path
    temp_dir = None
    if repo_path.startswith("http://") or repo_path.startswith("https://"):
        temp_dir = clone_repo(repo_path)
        repo_path = temp_dir

    try:
        dependencies = get_commit_dependencies(repo_path, since_date)
        mermaid_code = generate_mermaid_graph(dependencies)
        save_mermaid_graph(mermaid_code, args.output_file, args.mmdc_path)
        print(f"Dependency graph saved to {args.output_file}")
    finally:
        if temp_dir:
            # Cleanup temporary directory
            import shutil
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()


# pip install gitpython
# npm install -g @mermaid-js/mermaid-cli
# python dependency_visualizer.py \
#   --mmdc-path "/usr/local/bin/mmdc" \
#   --repo-path "/path/to/repo" \
#   --output-file "/path/to/output.png" \
#   --since-date "2024-01-01"



# python dependency_visualizer.py \
#   --mmdc-path "/usr/local/bin/mmdc" \
#   --repo-path "https://github.com/user/repository.git" \
#   --output-file "/path/to/output.png" \
#   --since-date "2024-01-01"
