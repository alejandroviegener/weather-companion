class AuthorID:
    def __init__(self, id: str):
        """
        id is not empty string, cannot have spaces
        """
        self._validate_id(id)
        self._id: str = id

    def _validate_id(self, id: str):
        """check if id is valid"""
        if not id:
            raise ValueError("The id cannot be empty.")
        if " " in id:
            raise ValueError("The id cannot contain spaces.")

    def __eq__(self, other):
        return self._id == other._id
