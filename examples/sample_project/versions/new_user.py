class User:
    """User data model."""

    def __init__(self, user_id: int, name: str, email: str, phone: str = None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone

    def get_details(self) -> dict:
        return {
            "id": self.user_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }

    def get_display_name(self) -> str:
        return f"{self.name} <{self.email}>"
