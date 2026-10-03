import ast
from pathlib import Path
from analyzer.scanner import RepositoryScanner


class SymbolResolver:
    """Builds and resolves symbols across a Python repository."""

    def __init__(self):
        self.symbols = {}

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
    
if __name__ == "__main__":

    scanner = RepositoryScanner(
        "examples/sample_project"
    )

    files = scanner.scan()

    resolver = SymbolResolver()

    for file_path in files:
        resolver.index_file(file_path)

    print("Symbols:")
    print("====================")

    for name, information in resolver.symbols.items():

        print(
            f"{name} "
            f"--[{information['type']}]--> "
            f"{information['file']}"
        )