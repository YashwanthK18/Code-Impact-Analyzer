from analyzer.scanner import RepositoryScanner
from analyzer.resolver import SymbolResolver
from analyzer.graph_builder import GraphBuilder
from analyzer.impact import ImpactAnalyzer
from analyzer.change_detector import ChangeDetector
from analyzer.git_provider import GitChangeProvider


class CodeAnalyzer:
    """Runs the complete code impact analysis pipeline."""

    def __init__(self, repository_path):
        self.repository_path = repository_path

    def build(self):

        scanner = RepositoryScanner(
            self.repository_path
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

        for file_path in files:

            resolver.index_variables(
                file_path
            )

        builder = GraphBuilder(
            resolver
        )

        graph = builder.build()

        return graph, resolver

    def find_changed_symbols(self):

        provider = GitChangeProvider(
            "."
        )

        changed_files = (
            provider.get_changed_files()
        )

        resolver = SymbolResolver()

        scanner = RepositoryScanner(
            self.repository_path
        )

        files = scanner.scan()

        for file_path in files:

            resolver.index_file(
                file_path
            )

        detector = ChangeDetector(
            resolver
        )

        changed_symbols = []

        for file_path in changed_files:

            if not file_path.startswith(
                self.repository_path.replace(
                    "\\",
                    "/"
                )
            ):

                if self.repository_path not in file_path:

                    continue

            try:

                old_source = (
                    provider.get_old_file(
                        file_path
                    )
                )

                new_source = (
                    provider.get_current_file(
                        file_path
                    )
                )

                symbols = detector.compare_source(
                    old_source,
                    new_source,
                    file_path
                )

                changed_symbols.extend(
                    symbols
                )

            except Exception as error:

                print(
                    f"Could not analyze "
                    f"{file_path}: {error}"
                )

        return changed_symbols

    def find_impact(self, symbol):

        graph, resolver = self.build()

        analyzer = ImpactAnalyzer(
            graph,
            resolver.symbols
        )

        return analyzer.find_impact(
            symbol
        )


if __name__ == "__main__":

    analyzer = CodeAnalyzer(
        "examples/sample_project"
    )

    changed_symbols = (
        analyzer.find_changed_symbols()
    )

    print("Code Impact Analysis")
    print("====================")

    print("\nChanged Symbols:")

    for symbol in changed_symbols:

        print(
            f"  {symbol}"
        )

    if not changed_symbols:

        print(
            "  No changed symbols found."
        )

    for changed_symbol in changed_symbols:

        affected = analyzer.find_impact(
            changed_symbol
        )

        print(
            f"\nImpact of: "
            f"{changed_symbol}"
        )

        if not affected:

            print(
                "  No potentially affected "
                "symbols found."
            )

            continue

        print(
            "\nPotentially affected:"
        )

        for item, information in affected.items():

            print(
                f"\n  {item}"
            )

            if "file" in information:

                print(
                    f"    File: "
                    f"{information['file']}"
                )

            if "line" in information:

                print(
                    f"    Line: "
                    f"{information['line']}"
                )

            print(
                f"    Relationship: "
                f"{information['relation']}"
            )

            print(
                "    Path:"
            )

            for step in information["path"]:

                print(
                    f"      ↓ {step}"
                )