import ast
from pathlib import Path


class ChangeDetector:

    def __init__(self, resolver):
        self.resolver = resolver

    def find_symbols(self, file_path):

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        module_name = self.resolver.get_module_name(
            file_path
        )

        symbols = {}

        for node in tree.body:

            if isinstance(node, ast.FunctionDef):

                symbol_name = (
                    f"{module_name}.{node.name}"
                )

                symbols[symbol_name] = ast.dump(
                    node,
                    include_attributes=False
                )

            elif isinstance(node, ast.ClassDef):

                class_name = (
                    f"{module_name}.{node.name}"
                )

                symbols[class_name] = ast.dump(
                    node,
                    include_attributes=False
                )

                for child in node.body:

                    if isinstance(
                        child,
                        ast.FunctionDef
                    ):

                        method_name = (
                            f"{module_name}."
                            f"{node.name}."
                            f"{child.name}"
                        )

                        symbols[method_name] = ast.dump(
                            child,
                            include_attributes=False
                        )

        return symbols

    def compare_files(
        self,
        old_file,
        new_file
    ):

        old_symbols = self.find_symbols(
            old_file
        )

        new_symbols = self.find_symbols(
            new_file
        )

        changed = []

        all_symbols = set(
            old_symbols
        ) | set(
            new_symbols
        )

        for symbol in all_symbols:

            old_code = old_symbols.get(
                symbol
            )

            new_code = new_symbols.get(
                symbol
            )

            if old_code != new_code:

                changed.append(
                    symbol
                )

        return changed


if __name__ == "__main__":

    from analyzer.scanner import RepositoryScanner
    from analyzer.resolver import SymbolResolver

    scanner = RepositoryScanner(
        "examples/sample_project"
    )

    files = scanner.scan()

    resolver = SymbolResolver()

    for file_path in files:

        resolver.index_file(
            file_path
        )

        resolver.index_imports(
            file_path
        )

    detector = ChangeDetector(
        resolver
    )

    changed = detector.compare_files(
        "examples/sample_project/versions/old_user.py",
        "examples/sample_project/versions/new_user.py"
    )

    print("Changed Symbols")
    print("====================")

    for symbol in changed:

        print(symbol)