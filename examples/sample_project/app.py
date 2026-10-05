from models.user import User
from services.order import OrderService


def run_app():
    """Sample application workflow."""
    user = User(user_id=1, name="Alice", email="alice@example.com")
    order_service = OrderService()
    order = order_service.create_order(user, item_name="Laptop", price=1200.0)
    print(f"Order completed successfully: {order}")


if __name__ == "__main__":
    run_app()
