class UserRepository:
    """
    Repository for authors.
    Contains api keys for registered users
    """

    def __init__(self):
        self._repository = []

    def add_user(self, user_id: str, api_key: str):
        self._repository.append((user_id, api_key))

    def get_api_key(self, user_id: str) -> str:
        for user in self._repository:
            if user[0] == user_id:
                return user[1]
        raise KeyError(f"User {user_id} not found")

    def get_user(self, api_key: str) -> str:
        for user in self._repository:
            if user[1] == api_key:
                return user[0]
        raise KeyError(f"User with api key {api_key} not found")
