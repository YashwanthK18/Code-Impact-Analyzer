from dataclasses import dataclass


@dataclass
class Dependency:
    """Represents a dependency between two code elements."""

    source: str
    target: str
    dependency_type: str