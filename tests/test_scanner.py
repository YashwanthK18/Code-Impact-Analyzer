from analyzer.scanner import RepositoryScanner


def test_scanner_finds_python_files():

    scanner = RepositoryScanner(
        "examples/sample_project"
    )

    files = scanner.scan()

    assert len(files) > 0

    for file_path in files:

        assert file_path.suffix == ".py"