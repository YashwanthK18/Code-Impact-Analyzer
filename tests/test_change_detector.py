from analyzer.change_detector import ChangeDetector
from analyzer.resolver import SymbolResolver


def test_changed_method():

    resolver = SymbolResolver()

    detector = ChangeDetector(
        resolver
    )

    old_source = """
class OrderService:

    def create_order(self, user):
        return "completed"
"""

    new_source = """
class OrderService:

    def create_order(self, user):
        return "complete"
"""

    changed = detector.compare_source(
        old_source,
        new_source,
        "examples/sample_project/services/order.py"
    )

    assert any(
        symbol.endswith(
            "services.order.OrderService.create_order"
        )
        for symbol in changed
    )