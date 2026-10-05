import ast
from pathlib import Path

from analyzer.resolver import SymbolResolver


class ChangeDetector:
    """Detects changed symbols between two versions of a file."""

    def __init__(self, resolver):
        self.resolver = resolver

    def extract_symbols(
        self,
        tree,
        file_path
    ):

        file_path = Path(file_path)

        module_name = self.resolver.get_module_name(
            file_path
        )

        symbols = {}

        for node in tree.body:

            if isinstance(
                node,
                ast.FunctionDef
            ):

                symbol_name = (
                    f"{module_name}.{node.name}"
                )

                symbols[symbol_name] = ast.dump(
                    node,
                    include_attributes=False
                )

            elif isinstance(
                node,
                ast.ClassDef
            ):

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

    def find_symbols(self, file_path):

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source_code
        )

        return self.extract_symbols(
            tree,
            file_path
        )

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

        all_symbols = (
            set(old_symbols) |
            set(new_symbols)
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

    def compare_source(
        self,
        old_source,
        new_source,
        file_path
    ):

        old_tree = ast.parse(
            old_source
        )

        new_tree = ast.parse(
            new_source
        )

        old_symbols = self.extract_symbols(
            old_tree,
            file_path
        )

        new_symbols = self.extract_symbols(
            new_tree,
            file_path
        )

        changed = []

        all_symbols = (
            set(old_symbols) |
            set(new_symbols)
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

    from analyzer.git_provider import (
        GitChangeProvider
    )

    provider = GitChangeProvider(
        "."
    )

    resolver = SymbolResolver()

    detector = ChangeDetector(
        resolver
    )

    changed_files = provider.get_changed_files()

    print("Git Change Detection")
    print("====================")

    for file_path in changed_files:

        print(
            f"\nFile: {file_path}"
        )

        try:

            old_source = provider.get_old_file(
                file_path
            )

            new_source = provider.get_current_file(
                file_path
            )

            changed_symbols = (
                detector.compare_source(
                    old_source,
                    new_source,
                    file_path
                )
            )

            for symbol in changed_symbols:

                print(
                    f"  Changed: {symbol}"
                )

        except Exception as error:

            print(
                f"  Error: {error}"
            )