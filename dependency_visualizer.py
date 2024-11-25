import argparse
import subprocess
import os
import tempfile
import shutil
from datetime import datetime

def get_commit_data(repo_path, since_date):
    """Извлекает данные о коммитах из всех веток git-репозитория."""
    # Получаем список веток с их последними коммитами
    branches_cmd = ["git", "-C", repo_path, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads/"]
    branches_result = subprocess.run(branches_cmd, capture_output=True, text=True, check=True)

    branch_mapping = {}
    for line in branches_result.stdout.splitlines():
        branch_name, commit_id = line.split()
        branch_mapping[commit_id] = branch_name

    # Извлекаем все коммиты из всех веток
    log_cmd = [
        "git", "-C", repo_path, "log", "--all",
        f"--since={since_date}",
        "--pretty=format:%H|%P|%an|%ad|%s",
        "--date=iso"
    ]
    result = subprocess.run(log_cmd, capture_output=True, text=True, check=True)

    commits = []
    for line in result.stdout.splitlines():
        if "|" in line:
            commit_data = line.split("|")
            commit_id = commit_data[0]
            parents = commit_data[1].split() if commit_data[1] else []
            author = commit_data[2]
            date = commit_data[3]
            message = commit_data[4]
            branch = branch_mapping.get(commit_id, None)
            commits.append({
                "id": commit_id,
                "parents": parents,
                "author": author,
                "date": date,
                "message": message,
                "branch": branch
            })

    return commits

def generate_mermaid_graph(commits):
    """Создает Mermaid-описание графа зависимостей всех веток."""
    graph = ["graph TD"]
    branch_heads = {}

    # Обрабатываем каждый коммит
    for commit in commits:
        sanitized_message = commit["message"].replace('"', "'").replace("<", "&lt;").replace(">", "&gt;")
        node_label = (
            f"Commit: {commit['id']}<br>"
            f"Author: {commit['author']}<br>"
            f"Date: {commit['date']}<br>"
            f"Message: {sanitized_message}"
        )
        graph.append(f'{commit["id"]}["{node_label}"]')

        # Связи с родительскими коммитами
        for parent in commit["parents"]:
            graph.append(f"{parent} --> {commit['id']}")

    return "\n".join(graph)



def save_mermaid_graph(mermaid_code, mermaid_cli, output_path):
    """Сохраняет Mermaid-граф в файл PNG."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mmd") as temp_file:
        temp_file.write(mermaid_code.encode("utf-8"))
        temp_file_path = temp_file.name

    try:
        cmd = [mermaid_cli, "-i", temp_file_path, "-o", output_path]
        subprocess.run(cmd, check=True)
    finally:
        os.remove(temp_file_path)


def main():
    parser = argparse.ArgumentParser(description="Визуализация графа зависимостей для git-репозитория.")
    parser.add_argument("--mermaid", required=True, help="Путь к программе Mermaid CLI.")
    parser.add_argument("--repo", help="Путь к локальному git-репозиторию.")
    parser.add_argument("--output", required=True, help="Путь к выходному PNG-файлу.")
    parser.add_argument("--since", required=True, help="Дата коммитов (например, 2024-01-01).")
    args = parser.parse_args()

    # Проверка аргументов
    if not shutil.which(args.mermaid):
        raise FileNotFoundError(f"Mermaid CLI не найден по пути {args.mermaid}.")
    # if args.url and args.repo:
    #     raise ValueError("Нельзя использовать одновременно --repo и --url.")
    if not args.repo:
        raise ValueError("Необходимо указать --repo.")
    if not datetime.strptime(args.since, "%Y-%m-%d"):
        raise ValueError(f"Некорректный формат даты: {args.since}.")

    # Работа с репозиторием
    temp_repo_path = None
    repo_path = args.repo

    # Основной процесс
    try:
        commits = get_commit_data(repo_path, args.since)
        mermaid_code = generate_mermaid_graph(commits)
        print("Generated Mermaid Code:\n", mermaid_code)

        save_mermaid_graph(mermaid_code, args.mermaid, args.output)
    finally:
        if temp_repo_path:
            shutil.rmtree(temp_repo_path)

    print(f"Граф зависимостей успешно сохранен в {args.output}.")


if __name__ == "__main__":
    main()


# python dependency_visualizer.py --mermaid C:\Users\mladi\AppData\Roaming\npm\mmdc.cmd --repo /path/to/repo --output graph.png --since 2024-01-01
# python git_viz.py --mermaid C:\Users\mladi\AppData\Roaming\npm\mmdc.cmd --url https://github.com/Rblba20/git_lab1_lesson2 --output graph.png --since 2016-01-01
# python git_viz.py --mermaid C:\Users\mladi\AppData\Roaming\npm\mmdc.cmd --repo pseudo-doom --output graph1.png --since 2021-04-14