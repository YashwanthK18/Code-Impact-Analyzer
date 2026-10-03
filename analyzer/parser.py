import ast
from pathlib import Path


class CodeParser:
    """Parses Python source code using Python's AST module."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def parse(self):
        """Parse the source file and return its AST."""

        source_code = self.file_path.read_text(encoding="utf-8")

        return ast.parse(source_code)

    def get_functions(self, tree):
        """Return top-level function definitions."""

        functions = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return functions

    def get_classes(self, tree):
        """Return all class definitions."""

        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return classes

    def get_methods(self, tree):
        """Return methods defined inside classes."""

        methods = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):

                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append({
                            "class": node.name,
                            "method": child.name
                        })

        return methods

    def get_imports(self, tree):
        """Return imported modules and names."""

        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""

                for alias in node.names:
                    imports.append(
                        f"{module}.{alias.name}"
                    )

        return imports

    def get_function_calls(self, tree):
        """Return function and method calls found in the file."""

        calls = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Call):

                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)

                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)

        return calls


if __name__ == "__main__":

    parser = CodeParser(
        "examples/sample_project/app.py"
    )

    tree = parser.parse()

    print("File:")
    print(parser.file_path)

    print("\nFunctions:")

    for function in parser.get_functions(tree):
        print(f"  {function}")

    print("\nClasses:")

    for class_name in parser.get_classes(tree):
        print(f"  {class_name}")

    print("\nMethods:")

    for method in parser.get_methods(tree):
        print(
            f"  {method['class']}.{method['method']}"
        )

    print("\nImports:")

    for imported_item in parser.get_imports(tree):
        print(f"  {imported_item}")

    print("\nFunction calls:")

    for call in parser.get_function_calls(tree):
        print(f"  {call}")