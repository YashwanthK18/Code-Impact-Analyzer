from analyzer.graph import DependencyGraph


class GraphBuilder:
    """Builds a dependency graph from resolved code information."""

    def __init__(self, resolver):
        self.resolver = resolver
        self.graph = DependencyGraph()

    def find_function_for_line(self, tree, line_number):
        """Find the function or method containing a line."""

        best_match = None
        best_start = -1

        for node in self._walk_functions(tree):

            start = node.lineno
            end = getattr(
                node,
                "end_lineno",
                start
            )

            if start <= line_number <= end:

                if start > best_start:
                    best_match = node
                    best_start = start

        return best_match

    def _walk_functions(self, tree):
        """Return all functions and methods in a tree."""

        import ast

        functions = []

        for node in ast.walk(tree):

            if isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                functions.append(node)

        return functions

    def get_symbol_name(self, file_path, node):
        """Convert an AST function into its symbol name."""

        module_name = self.resolver.get_module_name(
            file_path
        )

        import ast

        parent_class = None

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        for possible_class in ast.walk(tree):

            if not isinstance(
                possible_class,
                ast.ClassDef
            ):
                continue

            for child in possible_class.body:

                if child is node:

                    parent_class = possible_class.name

                    break

            if parent_class:
                break

        if parent_class:

            return (
                f"{module_name}."
                f"{parent_class}."
                f"{node.name}"
            )

        return (
            f"{module_name}."
            f"{node.name}"
        )

    def add_method_dependencies(self):

        import ast
        from pathlib import Path

        for file_path in self.resolver.imports:

            file_path = Path(file_path)

            source_code = file_path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(source_code)

            method_calls = (
                self.resolver.find_method_calls(
                    file_path
                )
            )

            for call in method_calls:

                line_number = call["line"]

                function_node = (
                    self.find_function_for_line(
                        tree,
                        line_number
                    )
                )

                if function_node is None:
                    continue

                source_symbol = (
                    self.get_symbol_name(
                        file_path,
                        function_node
                    )
                )

                self.graph.add_dependency(
                    source_symbol,
                    call["symbol"],
                    "calls"
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