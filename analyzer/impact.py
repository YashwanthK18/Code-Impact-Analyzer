from collections import defaultdict, deque


class ImpactAnalyzer:
    """Finds code that may be affected by a change."""

    def __init__(self, graph, symbols=None):
        self.graph = graph
        self.symbols = symbols or {}
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

                symbol_info = self.symbols.get(
                    dependent,
                    {}
                )

                distance = len(new_path) - 1

                if distance == 1:
                    impact_level = "direct"
                else:
                    impact_level = "indirect"

                affected[dependent] = {
                    "relation": relation,
                    "path": new_path,
                    "file": symbol_info.get("file"),
                    "line": symbol_info.get("line"),
                    "distance": distance,
                    "impact": impact_level
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

    symbols = {
        "app.run_app": {
            "file": "examples/sample_project/app.py",
            "line": 5
        },
        "services.order.OrderService": {
            "file": "examples/sample_project/services/order.py",
            "line": 5
        },
        "services.order.OrderService.create_order": {
            "file": "examples/sample_project/services/order.py",
            "line": 10
        }
    }

    analyzer = ImpactAnalyzer(
        graph,
        symbols
    )

    affected = analyzer.find_impact(
        "services.order.OrderService.create_order"
    )

    print("Impact Analysis")
    print("====================")

    for item, information in affected.items():

        print(item)
        print(
            f"  File: {information['file']}"
        )
        print(
            f"  Line: {information['line']}"
        )