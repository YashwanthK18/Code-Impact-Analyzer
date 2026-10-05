from pathlib import Path

from analyzer.scanner import RepositoryScanner
from analyzer.resolver import SymbolResolver
from analyzer.graph_builder import GraphBuilder
from analyzer.impact import ImpactAnalyzer
from analyzer.change_detector import ChangeDetector
from analyzer.git_provider import GitChangeProvider


class CodeAnalyzer:
    """Runs the complete code impact analysis pipeline."""

    def __init__(
        self,
        repository_path
    ):

        self.repository_path = str(
            Path(repository_path).resolve()
        )

    def build(self):

        scanner = RepositoryScanner(
            self.repository_path
        )

        files = scanner.scan()

        resolver = SymbolResolver(
            self.repository_path
        )

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
            self.repository_path
        )

        changed_files = (
            provider.get_changed_files()
        )

        resolver = SymbolResolver(
            self.repository_path
        )

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

        return sorted(
            set(changed_symbols)
        )

    def find_changed_symbols_between(
        self,
        old_commit,
        new_commit
    ):

        provider = GitChangeProvider(
            self.repository_path
        )

        changed_files = provider.get_changed_files(
            old_commit,
            new_commit
        )

        resolver = SymbolResolver(
            self.repository_path
        )

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

                old_source = provider.get_file_at_commit(
                    file_path,
                    old_commit
                )

                new_source = provider.get_file_at_commit(
                    file_path,
                    new_commit
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

        return sorted(
            set(changed_symbols)
        )

    def find_impact(
        self,
        symbol
    ):

        graph, resolver = self.build()

        analyzer = ImpactAnalyzer(
            graph,
            resolver.symbols
        )

        return analyzer.find_impact(
            symbol
        )

    def calculate_overall_risk(
        self,
        affected
    ):

        high_count = 0
        medium_count = 0
        low_count = 0

        affected_files = set()

        for information in affected.values():

            risk = information.get(
                "risk"
            )

            if risk == "HIGH":

                high_count += 1

            elif risk == "MEDIUM":

                medium_count += 1

            elif risk == "LOW":

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

        return {
            "risk": overall_risk,
            "affected_symbols": len(
                affected
            ),
            "affected_files": len(
                affected_files
            ),
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        }