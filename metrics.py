import ast
from pathlib import Path

root = Path("analyzer")

files = list(root.rglob("*.py"))

classes = 0
functions = 0
lines = 0

for file_path in files:
    source = file_path.read_text(encoding="utf-8")
    lines += len(source.splitlines())

    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes += 1

        elif isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            functions += 1

print("Python files:", len(files))
print("Lines of code:", lines)
print("Classes:", classes)
print("Functions/methods:", functions)