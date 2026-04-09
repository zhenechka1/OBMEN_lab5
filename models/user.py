class User:
    def __init__(self, user_id: int, username: str | None, chat_id: int):
        self.user_id = user_id
        self.username = username if username else "Unknown"
        self.chat_id = chat_id
