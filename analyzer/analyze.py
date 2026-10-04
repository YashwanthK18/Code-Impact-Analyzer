from analyzer.scanner import RepositoryScanner
from analyzer.resolver import SymbolResolver
from analyzer.graph_builder import GraphBuilder
from analyzer.impact import ImpactAnalyzer


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

        return graph

    def find_impact(self, symbol):

        graph = self.build()

        analyzer = ImpactAnalyzer(
            graph
        )

        return analyzer.find_impact(
            symbol
        )

if __name__ == "__main__":

    analyzer = CodeAnalyzer(
        "examples/sample_project"
    )

    changed_symbol = (
            "services.payment.PaymentService.process_payment"
    )

    affected = analyzer.find_impact(
        changed_symbol
    )

    print("Code Impact Analysis")
    print("====================")

    print(
        f"\nChanged symbol:\n"
        f"  {changed_symbol}"
    )

    print("\nPotentially affected:")

    for item, information in affected.items():

        print(
            f"\n  {item}"
        )

        print(
            f"    Relationship: "
            f"{information['relation']}"
        )

        print("    Path:")

        for step in information["path"]:

            print(
                f"      ↓ {step}"
            )