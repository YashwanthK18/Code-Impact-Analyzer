import ast
from pathlib import Path

from analyzer.dependency import Dependency
from analyzer.parser import CodeParser


class DependencyExtractor:
    """Extracts dependency relationships from Python source files."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.parser = CodeParser(file_path)

    def extract(self):
        """Extract dependencies from the source file."""

        tree = self.parser.parse()

        dependencies = []

        dependencies.extend(
            self._extract_import_dependencies(tree)
        )

        dependencies.extend(
            self._extract_call_dependencies(tree)
        )

        return dependencies

    def _extract_import_dependencies(self, tree):
        """Extract import dependencies."""

        dependencies = []

        for node in tree.body:

            if isinstance(node, ast.Import):

                for alias in node.names:

                    dependencies.append(
                        Dependency(
                            source=str(self.file_path),
                            target=alias.name,
                            dependency_type="imports"
                        )
                    )

            elif isinstance(node, ast.ImportFrom):

                module = node.module or ""

                for alias in node.names:

                    target = f"{module}.{alias.name}"

                    dependencies.append(
                        Dependency(
                            source=str(self.file_path),
                            target=target,
                            dependency_type="imports"
                        )
                    )

        return dependencies

    def _extract_call_dependencies(self, tree):
        """Extract function and method call dependencies."""

        dependencies = []

        for node in ast.walk(tree):

            if not isinstance(node, ast.Call):
                continue

            if isinstance(node.func, ast.Name):

                dependencies.append(
                    Dependency(
                        source=str(self.file_path),
                        target=node.func.id,
                        dependency_type="calls"
                    )
                )

            elif isinstance(node.func, ast.Attribute):

                dependencies.append(
                    Dependency(
                        source=str(self.file_path),
                        target=node.func.attr,
                        dependency_type="calls"
                    )
                )


        return dependencies


if __name__ == "__main__":

    extractor = DependencyExtractor(
        "examples/sample_project/app.py"
    )

    dependencies = extractor.extract()

    print("Dependencies:")
    print("====================")

    for dependency in dependencies:

        print(
            f"{dependency.source} "
            f"--[{dependency.dependency_type}]--> "
            f"{dependency.target}"
        )