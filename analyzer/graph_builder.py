import ast
from pathlib import Path

from analyzer.graph import DependencyGraph


class GraphBuilder:

    def __init__(self, resolver):
        self.resolver = resolver
        self.graph = DependencyGraph()
        self.files = []

    def get_function_name(self, file_path, line_number):

        file_path = Path(file_path)

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source)

        module_name = self.resolver.get_module_name(
            file_path
        )

        selected = None
        selected_start = -1
        selected_class = None

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

                if start > selected_start:
                    selected = node
                    selected_start = start

        if selected is None:
            return None

        for node in ast.walk(tree):

            if not isinstance(
                node,
                ast.ClassDef
            ):
                continue

            for child in node.body:

                if child is selected:
                    selected_class = node.name
                    break

            if selected_class:
                break

        if selected_class:

            return (
                f"{module_name}."
                f"{selected_class}."
                f"{selected.name}"
            )

        return (
            f"{module_name}."
            f"{selected.name}"
        )

    def find_calls(self, file_path):

        file_path = Path(file_path)

        if not file_path.exists():
            return []

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source)

        calls = []

        for node in ast.walk(tree):

            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                continue

            caller = self.get_function_name(
                file_path,
                node.lineno
            )

            if caller is None:
                continue

            for child in ast.walk(node):

                if not isinstance(
                    child,
                    ast.Call
                ):
                    continue

                function = child.func

                if not isinstance(
                    function,
                    ast.Attribute
                ):
                    continue

                method_name = function.attr

                if not isinstance(
                    function.value,
                    ast.Name
                ):
                    continue

                object_name = function.value.id

                target = None

                for symbol in self.resolver.symbols:

                    if not symbol.endswith(
                        "." + method_name
                    ):
                        continue

                    parts = symbol.split(".")

                    if len(parts) < 3:
                        continue

                    class_name = parts[-2]

                    if object_name.lower() == class_name.lower():
                        target = symbol
                        break

                if target is None:

                    matches = []

                    for symbol in self.resolver.symbols:

                        if symbol.endswith(
                            "." + method_name
                        ):
                            matches.append(symbol)

                    if len(matches) == 1:
                        target = matches[0]

                if target is None:
                    continue

                calls.append(
                    {
                        "source": caller,
                        "symbol": target,
                        "line": child.lineno
                    }
                )

        return calls

    def _get_file_symbols(self, file_path):

        result = []

        target_path = Path(
            file_path
        ).resolve()

        for symbol, information in self.resolver.symbols.items():

            symbol_file = information.get("file")

            if not symbol_file:
                continue

            try:

                symbol_path = Path(
                    symbol_file
                ).resolve()

                if symbol_path == target_path:
                    result.append(symbol)

            except Exception:
                continue

        return result

    def add_import_dependencies(self):

        for file_path in self.files:

            imports = self.resolver.imports.get(
                str(file_path),
                []
            )

            if isinstance(imports, dict):
                values = imports.values()
            else:
                values = imports

            source_symbols = self._get_file_symbols(
                file_path
            )

            for imported in values:

                if isinstance(imported, tuple):
                    imported = imported[0]

                if not isinstance(imported, str):
                    continue

                target = None

                if imported in self.resolver.symbols:
                    target = imported

                else:

                    matches = []

                    for symbol in self.resolver.symbols:

                        if symbol.endswith(
                            "." + imported
                        ):
                            matches.append(symbol)

                    if len(matches) == 1:
                        target = matches[0]

                if target is None:
                    continue

                for source in source_symbols:

                    self.graph.add_dependency(
                        source,
                        target,
                        "imports"
                    )

    def add_method_dependencies(self):

        for file_path in self.files:

            calls = self.find_calls(
                file_path
            )

            for call in calls:

                self.graph.add_dependency(
                    call["source"],
                    call["symbol"],
                    "calls"
                )

    def build(self, files=None):

        if files is not None:
            self.files = [
                Path(file_path)
                for file_path in files
            ]

        elif not self.files:

            for file_path in self.resolver.symbols.values():

                symbol_file = file_path.get("file")

                if symbol_file:
                    self.files.append(
                        Path(symbol_file)
                    )

            unique_files = []

            for file_path in self.files:

                if file_path not in unique_files:
                    unique_files.append(file_path)

            self.files = unique_files

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

    graph = builder.build(
        files
    )

    print("Dependency Graph")
    print("====================")

    for source, connections in graph.edges.items():

        print(f"\n{source}")

        for target, relation in connections:

            print(
                f"  --[{relation}]--> {target}"
            )