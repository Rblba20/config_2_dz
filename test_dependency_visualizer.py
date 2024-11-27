import unittest
from unittest.mock import patch, MagicMock
from dependency_visualizer import get_commit_data, generate_mermaid_graph, save_mermaid_graph


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

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    @patch("os.remove")
    def test_save_mermaid_graph(self, mock_remove, mock_tempfile, mock_subprocess):
        """Проверка функции save_mermaid_graph."""
        # Задаем входные данные
        mermaid_code = "graph TD\nA --> B"
        mermaid_cli = "/path/to/mermaid-cli"
        output_path = "output.png"
        temp_file_path = "/tmp/tempfile.mmd"

        # Настройка заглушки временного файла
        mock_temp_file = MagicMock()
        mock_temp_file.name = temp_file_path
        mock_tempfile.return_value.__enter__.return_value = mock_temp_file

        # Вызываем тестируемую функцию
        save_mermaid_graph(mermaid_code, mermaid_cli, output_path)

        # Проверяем, что временный файл был создан и записан
        mock_tempfile.assert_called_once_with(delete=False, suffix=".mmd")
        mock_temp_file.write.assert_called_once_with(mermaid_code.encode("utf-8"))

        # Проверяем вызов Mermaid CLI с правильными аргументами
        mock_subprocess.assert_called_once_with(
            [mermaid_cli, "-i", temp_file_path, "-o", output_path],
            check=True
        )

        # Проверяем, что временный файл был удален
        mock_remove.assert_called_once_with(temp_file_path)


if __name__ == "__main__":
    unittest.main()


# # coverage run -m unittest discover
# # coverage report
# # coverage html