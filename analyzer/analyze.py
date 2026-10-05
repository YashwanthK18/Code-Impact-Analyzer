from pathlib import Path

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

            resolver.index_parameters(
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

        changed_files = provider.get_changed_files()

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

        repository_path = Path(
            self.repository_path
        ).resolve()

        for file_path in changed_files:

            changed_path = Path(
                file_path
            ).resolve()

            try:

                changed_path.relative_to(
                    repository_path
                )

            except ValueError:

                continue

            if changed_path.suffix != ".py":

                continue

            try:

                old_source = provider.get_old_file(
                    file_path
                )

                new_source = provider.get_current_file(
                    file_path
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

    changed_symbols = analyzer.find_changed_symbols()

    print("Code Impact Analysis")
    print("====================")

    print("\nChanged Symbols:")

    if changed_symbols:

        for symbol in changed_symbols:

            print(
                f"  {symbol}"
            )

    else:

        print(
            "  No changed symbols found."
        )

    all_affected = {}

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

            all_affected[item] = information

            print(
                f"\n  {item}"
            )

            file_path = information.get(
                "file"
            )

            if file_path:

                print(
                    f"    File: {file_path}"
                )

            line_number = information.get(
                "line"
            )

            if line_number:

                print(
                    f"    Line: {line_number}"
                )

            relationship = information.get(
                "relation",
                "unknown"
            )

            print(
                f"    Relationship: "
                f"{relationship}"
            )

            impact = information.get(
                "impact",
                "UNKNOWN"
            )

            print(
                f"    Impact: {impact}"
            )

            impact_type = information.get(
                "impact_type"
            )

            if impact_type:

                print(
                    f"    Impact Type: "
                    f"{impact_type}"
                )

            print(
                "    Path:"
            )

            path = information.get(
                "path",
                []
            )

            for step in path:

                print(
                    f"      ↓ {step}"
                )

    high_count = 0
    medium_count = 0
    low_count = 0

    affected_files = set()

    for information in all_affected.values():

        impact = information.get(
            "impact"
        )

        if impact == "HIGH":

            high_count += 1

        elif impact == "MEDIUM":

            medium_count += 1

        elif impact == "LOW":

            low_count += 1

        file_path = information.get(
            "file"
        )

        if file_path:

            affected_files.add(
                file_path
            )

    if high_count > 0:

        overall_risk = "HIGH"

    elif medium_count > 0:

        overall_risk = "MEDIUM"

    elif low_count > 0:

        overall_risk = "LOW"

    else:

        overall_risk = "NONE"

    print("\n")
    print("Overall Risk")
    print("====================")

    print(
        f"Risk Level: {overall_risk}"
    )

    print(
        f"Changed Symbols: "
        f"{len(changed_symbols)}"
    )

    print(
        f"Affected Symbols: "
        f"{len(all_affected)}"
    )

    print(
        f"Affected Files: "
        f"{len(affected_files)}"
    )

    print(
        f"HIGH Impact: {high_count}"
    )

    print(
        f"MEDIUM Impact: {medium_count}"
    )

    print(
        f"LOW Impact: {low_count}"
    )