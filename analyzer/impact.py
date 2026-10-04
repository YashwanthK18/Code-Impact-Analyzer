from collections import defaultdict, deque


class ImpactAnalyzer:
    """Finds code that may be affected by a change."""

    def __init__(self, graph):
        self.graph = graph
        self.reverse_edges = defaultdict(set)

        self._build_reverse_graph()

    def _build_reverse_graph(self):
        """Create a graph pointing from dependencies to dependents."""

        for source, connections in self.graph.edges.items():

            for target, relation in connections:

                self.reverse_edges[target].add(
                    (source, relation)
                )

    def find_impact(self, changed_symbol):
        """Find affected symbols and the path to each one."""

        affected = {}
        queue = deque()

        queue.append(
            (changed_symbol, [changed_symbol])
        )

        while queue:

            current, path = queue.popleft()

            for dependent, relation in self.reverse_edges.get(
                current,
                set()
            ):

                if dependent in affected:
                    continue

                new_path = path + [dependent]

                affected[dependent] = {
                    "relation": relation,
                    "path": new_path
                }

                queue.append(
                    (dependent, new_path)
                )

        return affected

if __name__ == "__main__":

    from analyzer.graph import DependencyGraph

    graph = DependencyGraph()

    graph.add_dependency(
        "app.run_app",
        "services.order.OrderService",
        "uses"
    )

    graph.add_dependency(
        "services.order.OrderService",
        "services.order.OrderService.create_order",
        "calls"
    )

    analyzer = ImpactAnalyzer(
        graph
    )

    affected = analyzer.find_impact(
        "services.order.OrderService.create_order"
    )

    print("Impact Analysis")
    print("====================")

    for item in affected:
        print(item)