from analyzer.resolver import SymbolResolver


def test_module_name():

    resolver = SymbolResolver()

    name = resolver.get_module_name(
        "examples/sample_project/services/order.py"
    )

    assert name.endswith(
        "services.order"
    )