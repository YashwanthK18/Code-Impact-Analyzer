from models.user import User
from services.payment import PaymentService


class OrderService:
    """Handles order processing."""

    def __init__(self):
        self.orders = []
        self.payment_service = PaymentService()

    def create_order(self, user: User, item_name: str, price: float) -> dict:
        self.payment_service.process_payment(user, price)
        order = {
            "order_id": len(self.orders) + 1,
            "user": user.get_details(),
            "item": item_name,
            "price": price,
            "status": "completed",
        }
        self.orders.append(order)
        return order
