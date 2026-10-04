import ast
from pathlib import Path

from analyzer.graph import DependencyGraph


class GraphBuilder:
    """Builds a dependency graph from resolved code information."""

    def __init__(self, resolver):
        self.resolver = resolver
        self.graph = DependencyGraph()

    def get_function_name(self, file_path, line_number):
        """Find the function containing a specific line."""

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        module_name = self.resolver.get_module_name(
            file_path
        )

        best_function = None
        best_start = -1
        best_class = None

        for node in ast.walk(tree):

            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                continue

            start = node.lineno

            end = getattr(
                node,
                "end_lineno",
                start
            )

            if start <= line_number <= end:

                if start > best_start:

                    best_function = node
                    best_start = start

        if best_function is None:
            return None

        for node in ast.walk(tree):

            if not isinstance(
                node,
                ast.ClassDef
            ):
                continue

            for child in node.body:

                if child is best_function:

                    best_class = node.name
                    break

            if best_class:
                break

        if best_class:

            return (
                f"{module_name}."
                f"{best_class}."
                f"{best_function.name}"
            )

        return (
            f"{module_name}."
            f"{best_function.name}"
        )

    def add_import_dependencies(self):

        for file_path, imports in (
            self.resolver.imports.items()
        ):

            for local_name, full_name in (
                imports.items()
            ):

                self.graph.add_dependency(
                    str(file_path),
                    full_name,
                    "imports"
                )

    def add_method_dependencies(self):

        for file_path in self.resolver.imports:

            calls = self.resolver.find_method_calls(
                file_path
            )

            for call in calls:

                source_symbol = (
                    self.get_function_name(
                        file_path,
                        call["line"]
                    )
                )

                if source_symbol is None:
                    continue

                self.graph.add_dependency(
                    source_symbol,
                    call["symbol"],
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

    for source, connections in graph.edges.items():

        print(f"\n{source}")

        for target, relation in connections:

            print(
                f"  --[{relation}]--> {target}"
            )