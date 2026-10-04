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

        variable_info = variables.get(
            object_name
        )

        if not variable_info:
            return None

        class_name = variable_info["class"]

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

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        module_name = self.get_module_name(
            file_path
        )

        file_variables = {}

        for node in ast.walk(tree):

            if not isinstance(node, ast.Assign):
                continue

            value = node.value

            if not isinstance(value, ast.Call):
                continue

            if not isinstance(value.func, ast.Name):
                continue

            class_name = value.func.id

            imported_name = self.imports.get(
                str(file_path),
                {}
            ).get(class_name)

            if imported_name is None:
                continue

            for target in node.targets:

                if isinstance(target, ast.Name):

                    file_variables[target.id] = {
                        "type": "object",
                        "class": imported_name
                    }

                elif isinstance(target, ast.Attribute):

                    if isinstance(
                        target.value,
                        ast.Name
                    ):

                        object_name = (
                            f"{target.value.id}."
                            f"{target.attr}"
                        )

                        file_variables[object_name] = {
                            "type": "object",
                            "class": imported_name
                        }

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
   
    def find_method_calls(self, file_path):
        """Find and resolve object.method() calls."""

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        results = []

        for node in ast.walk(tree):

            if not isinstance(node, ast.Call):
                continue

            if not isinstance(node.func, ast.Attribute):
                continue

            object_node = node.func.value

            object_name = None

            if isinstance(
                object_node,
                ast.Name
            ):

                object_name = object_node.id

            elif isinstance(
                object_node,
                ast.Attribute
            ):

                if isinstance(
                    object_node.value,
                    ast.Name
                ):

                    object_name = (
                        f"{object_node.value.id}."
                        f"{object_node.attr}"
                    )

            if object_name is None:
                continue

            method_name = node.func.attr

            resolved = self.resolve_method(
                file_path,
                object_name,
                method_name
            )

            if resolved:

                results.append({
                    "object": object_name,
                    "method": method_name,
                    "symbol": resolved,
                    "line": node.lineno
                })

        return results

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

        for variable_name, information in variables.items():

            print(
                f"  {variable_name} "
                f"-> {information['class']}"
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
    
    print("\nResolved Method Calls:")
    print("====================")

    for file_path in files:

        method_calls = resolver.find_method_calls(
            file_path
        )

        print(f"\n{file_path}")

        for call in method_calls:

            print(
                f"  {call['object']}."
                f"{call['method']} "
                f"-> {call['symbol']}"
            )