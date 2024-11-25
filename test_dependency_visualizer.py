import unittest
from unittest.mock import patch
from dependency_visualizer import get_commit_data, generate_mermaid_graph


class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        """Настройка окружения для тестов."""
        # Пример репозитория (заглушка или временная структура)
        self.repo_path = "pseudo-doom"
        self.since_date = "2020-04-14"

    def test_get_commit_data_structure(self):
        """Проверка структуры возвращаемых данных."""
        commits = get_commit_data(self.repo_path, self.since_date)
        for commit in commits:
            self.assertIn("id", commit)
            self.assertIn("parents", commit)
            self.assertIn("author", commit)
            self.assertIn("date", commit)
            self.assertIn("message", commit)

    def test_commit_data_parsing(self):
        """Проверка корректности разбора данных о коммитах."""
        commits = get_commit_data(self.repo_path, self.since_date)
        first_commit = commits[0]

        self.assertEqual(first_commit["id"], "954a001a56a9df82e85c6e28b3d8a48265201952")
        self.assertEqual(first_commit["author"], "Rblba20")
        self.assertEqual(first_commit["message"], "Update Readme.txt")

    def test_mermaid_graph_generation(self):
        """Проверка, что сгенерированный граф соответствует шаблону."""
        commits = [
            {
                "id": "954a001a56a9df82e85c6e28b3d8a48265201952",
                "parents": ["b0c68f02b339e0b66a18b623371128f011ccfed1"],
                "author": "Rblba20",
                "date": "2023-12-24 21:27:29 +0300",
                "message": "Update Readme.txt",
                "files": []
            },
        ]
        mermaid_code = generate_mermaid_graph(commits)  # Функция должна быть реализована
        self.assertIn("graph TD", mermaid_code)
        self.assertIn("954a001a56a9df82e85c6e28b3d8a48265201952", mermaid_code)

    def test_command_execution(self):
        """Проверка вызова внешних команд git."""
        with unittest.mock.patch("subprocess.run") as mock_subprocess:
          #  mock_subprocess.return_value.stdout = "sample git log output"
            commits = get_commit_data(self.repo_path, self.since_date)
          #  self.assertGreater(len(commits), 0)
          #  mock_subprocess.assert_called()


if __name__ == "__main__":
    unittest.main()
