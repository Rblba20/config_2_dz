import os
import pytest
from dependency_visualizer import get_commit_dependencies, generate_mermaid_graph

@pytest.fixture
def sample_repo(tmp_path):
    repo_path = tmp_path / "test_repo"
    os.system(f"git init {repo_path}")
    os.chdir(repo_path)
    os.system("echo 'file1' > file1.txt && git add . && git commit -m 'Initial commit'")
    os.system("echo 'file2' > file2.txt && git add . && git commit -m 'Second commit'")
    return repo_path

def test_get_commit_dependencies(sample_repo):
    dependencies = get_commit_dependencies(sample_repo, "2023-01-01")
    assert len(dependencies) >= 2
    assert "file1.txt" in dependencies[0]["files"]

def test_generate_mermaid_graph():
    dependencies = [
        {"hash": "abc123", "files": ["file1.txt"], "parents": []},
        {"hash": "def456", "files": ["file2.txt"], "parents": ["abc123"]},
    ]
    graph = generate_mermaid_graph(dependencies)
    assert "abc123 --> def456" in graph
