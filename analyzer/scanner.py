from pathlib import Path


class RepositoryScanner:
    """Scans a repository and discovers source files."""

    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",          
        "node_modules",
        "dist",
        "build",
        ".env",
        ".env.example"
    }

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

            if any(
                ignored_directory in file_path.parts
                for ignored_directory in self.IGNORED_DIRECTORIES
            ):              
                continue

            source_files.append(file_path)

        return source_files