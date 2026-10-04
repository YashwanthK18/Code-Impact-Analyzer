from collections import defaultdict


class DependencyGraph:
    """Stores relationships between code symbols."""

    def __init__(self):
        self.edges = defaultdict(set)

    def add_dependency(self, source, target, relation):
        """Add a relationship between two symbols."""

        self.edges[source].add(
            (target, relation)
        )

    def get_dependencies(self, source):
        """Return everything directly used by a symbol."""

        return self.edges.get(
            source,
            set()
        )

    def show(self):
        """Display the dependency graph."""

        for source, connections in self.edges.items():

            print(f"\n{source}")

            for target, relation in connections:

                print(
                    f"  --[{relation}]--> {target}"
                )

if __name__ == "__main__":

    graph = DependencyGraph()

    graph.add_dependency(
        "app.run_app",
        "models.user.User",
        "uses"
    )

    graph.add_dependency(
        "app.run_app",
        "services.order.OrderService",
        "uses"
    )

    graph.add_dependency(
        "services.order.OrderService",
        "services.order.OrderService.create_order",
        "contains"
    )

    print("Dependency Graph")
    print("====================")

    graph.show()