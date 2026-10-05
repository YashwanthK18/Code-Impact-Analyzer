from collections import defaultdict, deque


class ImpactAnalyzer:
    """Finds code that may be affected by a changed symbol."""

    def __init__(
        self,
        graph,
        symbols=None
    ):

        self.graph = graph
        self.symbols = symbols or {}
        self.reverse_edges = defaultdict(set)

        self._build_reverse_graph()

    def _build_reverse_graph(self):

        for source, connections in self.graph.edges.items():

            for target, relation in connections:

                self.reverse_edges[target].add(
                    (
                        source,
                        relation
                    )
                )

    def _get_risk(
        self,
        distance
    ):

        if distance == 1:
            return "HIGH"

        if distance == 2:
            return "MEDIUM"

        return "LOW"

    def _get_confidence(
        self,
        distance
    ):

        if distance == 1:
            return 100

        if distance == 2:
            return 85

        if distance == 3:
            return 70

        return 60

    def _get_reason(
        self,
        relation,
        distance
    ):

        if distance == 1:

            if relation == "calls":

                return (
                    "Directly calls the changed symbol."
                )

            if relation == "uses":

                return (
                    "Directly depends on the changed symbol."
                )

            if relation == "imports":

                return (
                    "Directly imports the changed symbol."
                )

            return (
                "Has a direct dependency on the changed symbol."
            )

        if relation == "calls":

            return (
                "Indirectly depends on the changed symbol "
                "through a call chain."
            )

        if relation == "uses":

            return (
                "Indirectly depends on the changed symbol "
                "through another dependency."
            )

        return (
            "Indirectly depends on the changed symbol."
        )

    def find_impact(
        self,
        changed_symbol
    ):

        affected = {}

        queue = deque()

        queue.append(
            (
                changed_symbol,
                [changed_symbol]
            )
        )

        visited = {
            changed_symbol
        }

        while queue:

            current, path = queue.popleft()

            connections = (
                self.reverse_edges.get(
                    current,
                    set()
                )
            )

            for dependent, relation in connections:

                if dependent in visited:

                    continue

                visited.add(
                    dependent
                )

                new_path = (
                    path +
                    [dependent]
                )

                distance = (
                    len(new_path) - 1
                )

                impact = (
                    "direct"
                    if distance == 1
                    else "indirect"
                )

                risk = self._get_risk(
                    distance
                )

                confidence = self._get_confidence(
                    distance
                )

                reason = self._get_reason(
                    relation,
                    distance
                )

                symbol_info = self.symbols.get(
                    dependent,
                    {}
                )

                affected[dependent] = {
                    "relation": relation,
                    "path": new_path,
                    "file": symbol_info.get(
                        "file"
                    ),
                    "line": symbol_info.get(
                        "line"
                    ),
                    "distance": distance,
                    "impact": impact,
                    "risk": risk,
                    "confidence": confidence,
                    "reason": reason
                }

                queue.append(
                    (
                        dependent,
                        new_path
                    )
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

    graph.add_dependency(
        "services.order.OrderService.create_order",
        "models.user.User.get_details",
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
            "line": 12
        }
    }

    analyzer = ImpactAnalyzer(
        graph,
        symbols
    )

    affected = analyzer.find_impact(
        "models.user.User.get_details"
    )

    print("Impact Analysis")
    print("====================")

    for item, information in affected.items():

        print(item)

        print(
            f"  File: "
            f"{information.get('file')}"
        )

        print(
            f"  Line: "
            f"{information.get('line')}"
        )

        print(
            f"  Relationship: "
            f"{information.get('relation')}"
        )

        print(
            f"  Impact: "
            f"{information.get('impact')}"
        )

        print(
            f"  Risk: "
            f"{information.get('risk')}"
        )

        print(
            f"  Confidence: "
            f"{information.get('confidence')}%"
        )

        print(
            f"  Reason: "
            f"{information.get('reason')}"
        )

        print("  Path:")

        for step in information.get(
            "path",
            []
        ):

            print(
                f"    ↓ {step}"
            )