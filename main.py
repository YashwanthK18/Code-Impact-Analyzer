import sys

from analyzer.scanner import RepositoryScanner


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <repository-path>")
        return

    repository_path = sys.argv[1]

    scanner = RepositoryScanner(repository_path)

    try:
        source_files = scanner.scan()

        print("\nCode Impact Analyzer")
        print("====================")
        print(f"Repository: {repository_path}")

        print("\nPython source files:")

        for file_path in source_files:
            print(f"  {file_path}")

        print(f"\nTotal Python files: {len(source_files)}")

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"\nError: {error}")


if __name__ == "__main__":
    main()