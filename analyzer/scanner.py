from pathlib import Path


class RepositoryScanner:
    """Scans a repository and discovers source files."""

    def __init__(self, repository_path):
        self.repository_path = Path(repository_path)

    def scan(self):
        """Find all Python source files in the repository."""

        if not self.repository_path.exists():
            raise FileNotFoundError(
                f"Repository not found: {self.repository_path}"
            )

        if not self.repository_path.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {self.repository_path}"
            )

        source_files = []

        for file_path in self.repository_path.rglob("*.py"):
            source_files.append(file_path)

        return source_files
