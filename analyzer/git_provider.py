from pathlib import Path
import subprocess


class GitChangeProvider:
    """Provides Git file changes and file contents."""

    def __init__(self, repository_path):
        self.repository_path = Path(
            repository_path
        ).resolve()

    def get_repository_root(self):

        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "--show-toplevel"
            ],
            cwd=self.repository_path,
            capture_output=True,
            text=True,
            check=True
        )

        return Path(
            result.stdout.strip()
        ).resolve()

    def _git_root(self):

        return self.get_repository_root()

    def _relative_git_path(self, file_path):

        file_path = Path(
            file_path
        ).resolve()

        root = self.get_repository_root()

        return file_path.relative_to(
            root
        )

    def get_changed_files(
        self,
        from_commit="HEAD",
        to_commit=None
    ):

        if to_commit is None:

            command = [
                "git",
                "diff",
                "--name-only",
                from_commit
            ]

        else:

            command = [
                "git",
                "diff",
                "--name-only",
                from_commit,
                to_commit
            ]

        result = subprocess.run(
            command,
            cwd=self.repository_path,
            capture_output=True,
            text=True,
            check=True
        )

        root = self.get_repository_root()
        files = []

        for line in result.stdout.splitlines():

            relative_path = Path(
                line.strip()
            )

            if not str(relative_path):
                continue

            full_path = (
                root / relative_path
            ).resolve()

            try:

                full_path.relative_to(
                    self.repository_path
                )

            except ValueError:

                continue

            if full_path.suffix != ".py":
                continue

            files.append(
                str(full_path)
            )

        return files

    def get_changed_files_between(
        self,
        from_commit,
        to_commit
    ):

        return self.get_changed_files(
            from_commit,
            to_commit
        )

    def get_file_at_commit(
        self,
        file_path,
        commit
    ):

        file_path = Path(
            file_path
        ).resolve()

        root = self.get_repository_root()

        relative_path = file_path.relative_to(
            root
        )

        result = subprocess.run(
            [
                "git",
                "show",
                f"{commit}:{relative_path.as_posix()}"
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout

    def get_old_file(
        self,
        file_path
    ):

        return self.get_file_at_commit(
            file_path,
            "HEAD"
        )

    def get_current_file(
        self,
        file_path
    ):

        file_path = Path(
            file_path
        ).resolve()

        return file_path.read_text(
            encoding="utf-8"
        )


if __name__ == "__main__":

    provider = GitChangeProvider(
        "examples/sample_project"
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