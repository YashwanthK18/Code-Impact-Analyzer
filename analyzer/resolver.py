import ast
from pathlib import Path
from analyzer.scanner import RepositoryScanner


class SymbolResolver:
    """Builds and resolves symbols across a Python repository."""

    def __init__(self):
        self.symbols = {}
        self.imports = {}
        self.variables = {}
        self.parameters = {}

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
                    "name": node.name,
                    "line": node.lineno
                }

            elif isinstance(node, ast.ClassDef):

                symbol_name = (
                    f"{module_name}.{node.name}"
                )

                self.symbols[symbol_name] = {
                    "type": "class",
                    "file": str(file_path),
                    "name": node.name,
                    "line": node.lineno
                }

                for child in node.body:

                    if isinstance(
                        child,
                        ast.FunctionDef
                    ):

                        method_name = (
                            f"{module_name}."
                            f"{node.name}."
                            f"{child.name}"
                        )

                        self.symbols[method_name] = {
                            "type": "method",
                            "file": str(file_path),
                            "class": node.name,
                            "name": child.name,
                            "line": child.lineno
                        }

    def get_module_name(self, file_path):

        file_path = Path(file_path)

        sample_root = Path(
            "examples/sample_project"
        )

        try:

            relative_path = file_path.relative_to(
                sample_root
            )

        except ValueError:

            relative_path = file_path

        module_parts = list(
            relative_path.parts
        )

        if not module_parts:
            return ""

        module_parts[-1] = module_parts[-1].replace(
            ".py",
            ""
        )

        return ".".join(module_parts)
    
    def resolve_method(
        self,
        file_path,
        object_name,
        method_name
    ):
        """Resolve a method call using the object's known type."""

        file_path = str(file_path)

        variables = self.variables.get(
            file_path,
            {}
        )

        variable_info = variables.get(
            object_name
        )

        if variable_info:

            class_name = variable_info[
                "class"
            ]

            method_symbol = (
                f"{class_name}.{method_name}"
            )

            symbol = self.symbols.get(
                method_symbol
            )

            if (
                symbol
                and symbol["type"] == "method"
            ):
                return method_symbol

        for function_name, parameters in self.parameters.get(
            file_path,
            {}
        ).items():

            parameter_type = parameters.get(
                object_name
            )

            if parameter_type:

                method_symbol = (
                    f"{parameter_type}."
                    f"{method_name}"
                )

                symbol = self.symbols.get(
                    method_symbol
                )

                if (
                    symbol
                    and symbol["type"] == "method"
                ):
                    return method_symbol

        return None

    def index_variables(self, file_path):

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        file_variables = {}

        for node in ast.walk(tree):

            if not isinstance(
                node,
                ast.Assign
            ):
                continue

            value = node.value

            if not isinstance(
                value,
                ast.Call
            ):
                continue

            if not isinstance(
                value.func,
                ast.Name
            ):
                continue

            class_name = value.func.id

            imported_name = self.imports.get(
                str(file_path),
                {}
            ).get(class_name)

            if imported_name is None:
                continue

            for target in node.targets:

                if isinstance(
                    target,
                    ast.Name
                ):

                    file_variables[
                        target.id
                    ] = {
                        "type": "object",
                        "class": imported_name
                    }

                elif isinstance(
                    target,
                    ast.Attribute
                ):

                    if isinstance(
                        target.value,
                        ast.Name
                    ):

                        object_name = (
                            f"{target.value.id}."
                            f"{target.attr}"
                        )

                        file_variables[
                            object_name
                        ] = {
                            "type": "object",
                            "class": imported_name
                        }

        self.variables[
            str(file_path)
        ] = file_variables

    def index_parameters(self, file_path):

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        module_name = self.get_module_name(
            file_path
        )

        file_parameters = {}

        for node in ast.walk(tree):

            if not isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            ):
                continue

            function_name = node.name

            parent_class = None

            for parent in ast.walk(tree):

                if not isinstance(
                    parent,
                    ast.ClassDef
                ):
                    continue

                for child in parent.body:

                    if child is node:

                        parent_class = parent.name
                        break

                if parent_class:
                    break

            if parent_class:

                function_symbol = (
                    f"{module_name}."
                    f"{parent_class}."
                    f"{function_name}"
                )

            else:

                function_symbol = (
                    f"{module_name}."
                    f"{function_name}"
                )

            arguments = node.args.args

            parameter_info = {}

            for argument in arguments:

                if argument.annotation is None:
                    continue

                if isinstance(
                    argument.annotation,
                    ast.Name
                ):

                    type_name = (
                        argument.annotation.id
                    )

                elif isinstance(
                    argument.annotation,
                    ast.Attribute
                ):

                    type_name = (
                        argument.annotation.attr
                    )

                else:
                    continue

                imported_type = self.imports.get(
                    str(file_path),
                    {}
                ).get(type_name)

                if imported_type:

                    parameter_info[
                        argument.arg
                    ] = imported_type

            file_parameters[
                function_symbol
            ] = parameter_info

        self.parameters[
            str(file_path)
        ] = file_parameters

    def index_imports(self, file_path):
        """Extract imported names from a Python file."""

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        file_imports = {}

        for node in tree.body:

            if isinstance(
                node,
                ast.ImportFrom
            ):

                module = node.module or ""

                for alias in node.names:

                    local_name = (
                        alias.asname
                        or alias.name
                    )

                    full_name = (
                        f"{module}."
                        f"{alias.name}"
                    )

                    file_imports[
                        local_name
                    ] = full_name

            elif isinstance(
                node,
                ast.Import
            ):

                for alias in node.names:

                    local_name = (
                        alias.asname
                        or alias.name
                    )

                    file_imports[
                        local_name
                    ] = alias.name

        self.imports[
            str(file_path)
        ] = file_imports

    def find_method_calls(self, file_path):
        """Find and resolve object.method() calls."""

        file_path = Path(file_path)

        source_code = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source_code)

        results = []

        for node in ast.walk(tree):

            if not isinstance(
                node,
                ast.Call
            ):
                continue

            if not isinstance(
                node.func,
                ast.Attribute
            ):
                continue

            object_node = node.func.value

            if not isinstance(
                object_node,
                ast.Name
            ):
                continue

            object_name = object_node.id
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

    print("Symbols:")
    print("====================")

    for name, information in resolver.symbols.items():

        print(
            f"{name} "
            f"--[{information['type']}]--> "
            f"{information['file']} "
            f"(line {information['line']})"
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

    for file_path in resolver.imports:

        print(f"\n{file_path}")

        calls = resolver.find_method_calls(
            file_path
        )

        for call in calls:

            print(
                f"  {call['object']}."
                f"{call['method']}"
            )

    print("\nResolved Method Calls:")
    print("====================")

    for file_path in resolver.imports:

        calls = resolver.find_method_calls(
            file_path
        )

        if calls:
            print(f"\n{file_path}")

        for call in calls:

            print(
                f"  {call['object']}."
                f"{call['method']} "
                f"-> {call['symbol']}"
            )

    print("\nParameters:")
    print("====================")

    for file_path, functions in resolver.parameters.items():

        print(f"\n{file_path}")

        for function_name, parameters in functions.items():

            if not parameters:
                continue

            print(
                f"  {function_name}"
            )

            for parameter_name, parameter_type in parameters.items():

                print(
                    f"    {parameter_name} "
                    f"-> {parameter_type}"
                )