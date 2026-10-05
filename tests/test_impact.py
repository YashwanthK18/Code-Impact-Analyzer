from analyzer.graph import DependencyGraph
from analyzer.impact import ImpactAnalyzer


def test_direct_impact():

    graph = DependencyGraph()

    graph.add_dependency(
        "app.run_app",
        "services.order.OrderService.create_order",
        "calls"
    )

    symbols = {
        "app.run_app": {
            "file": "app.py",
            "line": 5
        },
        "services.order.OrderService.create_order": {
            "file": "order.py",
            "line": 10
        }
    }

    analyzer = ImpactAnalyzer(
        graph,
        symbols
    )

    result = analyzer.find_impact(
        "services.order.OrderService.create_order"
    )

    assert "app.run_app" in result

    assert result["app.run_app"]["distance"] == 1

    assert result["app.run_app"]["impact"] == "direct"


def test_indirect_impact():

    graph = DependencyGraph()

    graph.add_dependency(
        "services.order.OrderService.create_order",
        "models.user.User.get_details",
        "calls"
    )

    graph.add_dependency(
        "app.run_app",
        "services.order.OrderService.create_order",
        "calls"
    )

    symbols = {
        "models.user.User.get_details": {
            "file": "user.py",
            "line": 10
        },
        "services.order.OrderService.create_order": {
            "file": "order.py",
            "line": 12
        },
        "app.run_app": {
            "file": "app.py",
            "line": 5
        }
    }

    analyzer = ImpactAnalyzer(
        graph,
        symbols
    )

    result = analyzer.find_impact(
        "models.user.User.get_details"
    )

    assert "services.order.OrderService.create_order" in result

    assert "app.run_app" in result

    assert (
        result["services.order.OrderService.create_order"]["distance"]
        == 1
    )

    assert (
        result["app.run_app"]["distance"]
        == 2
    )