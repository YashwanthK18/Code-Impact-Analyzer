from analyzer.graph import DependencyGraph


class GraphBuilder:
    """Builds a dependency graph from resolved code information."""

    def __init__(self, resolver):
        self.resolver = resolver
        self.graph = DependencyGraph()

    def add_import_dependencies(self):

        for file_path, imports in self.resolver.imports.items():

            source_file = file_path

            for local_name, full_name in imports.items():

                self.graph.add_dependency(
                    source_file,
                    full_name,
                    "imports"
                )

    def add_method_dependencies(self):

        for file_path in self.resolver.imports:

            method_calls = (
                self.resolver.find_method_calls(
                    file_path
                )
            )

            for call in method_calls:

                method_symbol = call["symbol"]

                self.graph.add_dependency(
                    file_path,
                    method_symbol,
                    "calls"
                )

    def build(self):

        self.add_import_dependencies()
        self.add_method_dependencies()

        return self.graph

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

    for file_path in files:

        resolver.index_variables(
            file_path
        )

    builder = GraphBuilder(
        resolver
    )

    graph = builder.build()

    print("Dependency Graph")
    print("====================")

    graph.show()