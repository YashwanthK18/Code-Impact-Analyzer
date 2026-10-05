from analyzer.graph import DependencyGraph


def test_add_dependency():

    graph = DependencyGraph()

    graph.add_dependency(
        "app.run_app",
        "services.order.OrderService.create_order",
        "calls"
    )

    assert "app.run_app" in graph.edges

    assert (
        "services.order.OrderService.create_order",
        "calls"
    ) in graph.edges["app.run_app"]


def test_multiple_dependencies():

    graph = DependencyGraph()

    graph.add_dependency(
        "app.run_app",
        "services.order.OrderService",
        "uses"
    )

    graph.add_dependency(
        "app.run_app",
        "models.user.User",
        "uses"
    )

    assert len(graph.edges["app.run_app"]) == 2