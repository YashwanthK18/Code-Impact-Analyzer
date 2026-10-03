from models.user import User


class PaymentService:
    """Handles payment transactions."""

    def __init__(self):
        self.transactions = []

    def process_payment(self, user: User, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        transaction = {
            "user_id": user.user_id,
            "amount": amount,
            "status": "completed",
        }
        self.transactions.append(transaction)
        return True
