from pathlib import Path
import subprocess


class GitChangeProvider:
    """Gets changed Python files and their Git versions."""

    def __init__(self, repository_path):
        self.repository_path = Path(repository_path)

    def get_changed_files(self):

        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                "HEAD"
            ],
            cwd=self.repository_path,
            capture_output=True,
            text=True,
            check=True
        )

        files = []

        for line in result.stdout.splitlines():

            file_path = line.strip()

            if file_path.endswith(".py"):
                files.append(file_path)

        return files

    def get_old_file(self, file_path):

        result = subprocess.run(
            [
                "git",
                "show",
                f"HEAD:{file_path}"
            ],
            cwd=self.repository_path,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout

    def get_current_file(self, file_path):

        full_path = (
            self.repository_path /
            file_path
        )

        return full_path.read_text(
            encoding="utf-8"
        )


if __name__ == "__main__":

    provider = GitChangeProvider(
        "."
    )

    changed_files = provider.get_changed_files()

    print("Changed Python Files")
    print("====================")

    for file_path in changed_files:

        print(file_path)

        try:

            old_source = provider.get_old_file(
                file_path
            )

            print("\nOld version:")
            print(old_source)

        except subprocess.CalledProcessError:

            print(
                "\nNo previous Git version available."
            )