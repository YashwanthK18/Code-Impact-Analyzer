class User:
    """User data model."""

    def __init__(self, user_id: int, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email

    def get_details(self) -> dict:
        return {
            "id": self.user_id,
            "name": self.name,
            "email": self.email,
        }
