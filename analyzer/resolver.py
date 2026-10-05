import ast
from pathlib import Path
from collections import defaultdict


class SymbolResolver:

    def __init__(self, repository_path=None):

        self.repository_path = (
            Path(repository_path).resolve()
            if repository_path
            else None
        )

        self.files = {}
        self.imports = defaultdict(list)
        self.variables = defaultdict(dict)
        self.symbols = {}

    def set_repository_root(self, repository_path):

        self.repository_path = Path(
            repository_path
        ).resolve()

    def get_module_name(self, file_path):

        file_path = Path(
            file_path
        ).resolve()

        if self.repository_path:

            try:

                relative_path = file_path.relative_to(
                    self.repository_path
                )

            except ValueError:

                relative_path = file_path

        else:

            relative_path = file_path

            parts = list(
                relative_path.parts
            )

            if "examples" in parts:

                index = parts.index(
                    "examples"
                )

                parts = parts[index + 2:]

                relative_path = Path(
                    *parts
                )

        parts = list(
            relative_path.parts
        )

        if parts and parts[-1].endswith(".py"):

            parts[-1] = parts[-1][:-3]

        if parts and parts[-1] == "__init__":

            parts.pop()

        return ".".join(parts)

    def index_file(self, file_path):

        file_path = Path(
            file_path
        ).resolve()

        self.files[str(file_path)] = (
            self.get_module_name(file_path)
        )

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        module_name = self.get_module_name(
            file_path
        )

        for node in tree.body:

            if isinstance(
                node,
                ast.FunctionDef
            ):

                name = (
                    f"{module_name}.{node.name}"
                )

                self.symbols[name] = {
                    "file": str(file_path),
                    "line": node.lineno
                }

            elif isinstance(
                node,
                ast.AsyncFunctionDef
            ):

                name = (
                    f"{module_name}.{node.name}"
                )

                self.symbols[name] = {
                    "file": str(file_path),
                    "line": node.lineno
                }

            elif isinstance(
                node,
                ast.ClassDef
            ):

                class_name = (
                    f"{module_name}.{node.name}"
                )

                self.symbols[class_name] = {
                    "file": str(file_path),
                    "line": node.lineno
                }

                for child in node.body:

                    if isinstance(
                        child,
                        (
                            ast.FunctionDef,
                            ast.AsyncFunctionDef
                        )
                    ):

                        method_name = (
                            f"{module_name}."
                            f"{node.name}."
                            f"{child.name}"
                        )

                        self.symbols[method_name] = {
                            "file": str(file_path),
                            "line": child.lineno
                        }

    def index_imports(self, file_path):

        file_path = Path(
            file_path
        ).resolve()

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        module_name = self.get_module_name(
            file_path
        )

        for node in tree.body:

            if isinstance(
                node,
                ast.Import
            ):

                for item in node.names:

                    self.imports[module_name].append(
                        (
                            item.name,
                            item.asname
                        )
                    )

            elif isinstance(
                node,
                ast.ImportFrom
            ):

                if node.module:

                    for item in node.names:

                        imported_name = (
                            f"{node.module}."
                            f"{item.name}"
                        )

                        self.imports[module_name].append(
                            (
                                imported_name,
                                item.asname
                            )
                        )

    def index_variables(self, file_path):

        file_path = Path(
            file_path
        ).resolve()

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source
        )

        module_name = self.get_module_name(
            file_path
        )

        for node in ast.walk(tree):

            if not isinstance(
                node,
                ast.Assign
            ):

                continue

            if len(node.targets) != 1:

                continue

            target = node.targets[0]

            if not isinstance(
                target,
                ast.Name
            ):

                continue

            self.variables[module_name][
                target.id
            ] = {
                "line": node.lineno
            }