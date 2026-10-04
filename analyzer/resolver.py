import ast
from pathlib import Path
from analyzer.scanner import RepositoryScanner


class SymbolResolver:
    """Builds and resolves symbols across a Python repository."""

    def __init__(self):
        self.symbols = {}
        self.imports = {}
        self.variables = {}

    def add_symbol(self, name, symbol_type, file_path):
        """Add a symbol to the symbol table."""

        self.symbols[name] = {
            "type": symbol_type,
            "file": str(file_path)
        }

    def get_symbol(self, name):
        """Find a symbol by name."""

        return self.symbols.get(name)

    def index_file(self, file_path):
        """Extract symbols from a Python file."""

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
    )

        tree = ast.parse(source_code)

        module_name = self.get_module_name(
            file_path
        )

        for node in tree.body:

            if isinstance(node, ast.FunctionDef):

                symbol_name = (
                    f"{module_name}.{node.name}"
                )

                self.symbols[symbol_name] = {
                    "type": "function",
                    "file": str(file_path),
                    "name": node.name
                }

            elif isinstance(node, ast.ClassDef):

                symbol_name = (
                    f"{module_name}.{node.name}"
                )

                self.symbols[symbol_name] = {
                    "type": "class",
                    "file": str(file_path),
                    "name": node.name
                }

                for child in node.body:

                    if isinstance(child, ast.FunctionDef):

                        method_name = (
                            f"{module_name}."
                            f"{node.name}."
                            f"{child.name}"
                        )

                        self.symbols[method_name] = {
                            "type": "method",
                            "file": str(file_path),
                            "class": node.name,
                            "name": child.name
                        }

    def get_module_name(self, file_path):
        """Convert a Python file path into a module name."""

        file_path = Path(file_path)

        relative_path = file_path.relative_to(
            Path("examples/sample_project")
        )

        module_parts = list(relative_path.parts)

        module_parts[-1] = module_parts[-1].replace(
            ".py",
            ""
        )

        return ".".join(module_parts)
    
    def resolve_method(self, file_path, object_name, method_name):
        """Resolve a method call using the object's known type."""

        file_path = str(file_path)

        variables = self.variables.get(
            file_path,
            {}
        )

        class_name = variables.get(object_name)

        if not class_name:
            return None

        method_symbol = (
            f"{class_name}.{method_name}"
        )

        symbol = self.symbols.get(
            method_symbol
        )

        if symbol and symbol["type"] == "method":
            return method_symbol

        return None
    
    def index_variables(self, file_path):
        """Track variables created from known classes."""

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        file_variables = {}

        for node in ast.walk(tree):

            if not isinstance(node, ast.Assign):
                continue

            if not isinstance(node.value, ast.Call):
                continue

            if not isinstance(node.value.func, ast.Name):
                continue

            variable_name = None

            if len(node.targets) == 1:
                target = node.targets[0]

                if isinstance(target, ast.Name):
                    variable_name = target.id

            if variable_name is None:
                continue

            class_name = node.value.func.id

            imported_name = self.imports.get(
                str(file_path),
                {}
            ).get(class_name)

            if imported_name:
                file_variables[variable_name] = imported_name

        self.variables[str(file_path)] = file_variables

    def index_imports(self, file_path):
        """Extract imported names from a Python file."""

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        file_imports = {}

        for node in tree.body:

            if isinstance(node, ast.ImportFrom):

                module = node.module or ""

                for alias in node.names:

                    local_name = alias.asname or alias.name

                    full_name = (
                        f"{module}.{alias.name}"
                    )

                    file_imports[local_name] = full_name

            elif isinstance(node, ast.Import):

                for alias in node.names:

                    local_name = alias.asname or alias.name

                    file_imports[local_name] = alias.name

        self.imports[str(file_path)] = file_imports


if __name__ == "__main__":

    scanner = RepositoryScanner(
        "examples/sample_project"
    )

    files = scanner.scan()

    resolver = SymbolResolver()

    for file_path in files:
        resolver.index_file(file_path)
        resolver.index_imports(file_path)
        resolver.index_variables(file_path)

    print("Symbols:")
    print("====================")

    for name, information in resolver.symbols.items():

        print(
            f"{name} "
            f"--[{information['type']}]--> "
            f"{information['file']}"
        )
    
    print("\nImports:")
    print("====================")

    for file_path, imports in resolver.imports.items():

        print(f"\n{file_path}")

        for local_name, full_name in imports.items():

            print(
                f"  {local_name} -> {full_name}"
            )
    
    print("\nVariables:")
    print("====================")

    for file_path, variables in resolver.variables.items():

        print(f"\n{file_path}")

    for variable_name, symbol_name in variables.items():

        print(
            f"  {variable_name} -> {symbol_name}"
        )

    print("\nMethod Calls:")
    print("====================")

    for file_path, imports in resolver.imports.items():

        file_path_str = str(file_path)

        print(f"\n{file_path_str}")

        for local_name, full_name in imports.items():

            if "service" not in local_name:
                continue

            method_symbol = resolver.resolve_method(
                file_path,
                local_name,
                "process_payment"
            )

            if method_symbol:

                print(
                    f"  {local_name}.process_payment "
                    f"--> {method_symbol}"
                )