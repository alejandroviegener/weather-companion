class Bookmark:
    """Class to represent a bookmarked. Just a name"""

    def __init__(self, name: str):
        name = self._check_valid_name(name)
        self._name = name

    def name(self) -> str:
        return self._name

    def _check_valid_name(self, name) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Name can not be blank")
        if " " in name:
            raise ValueError("Name can not contain spaces")
        if not name.isalnum():
            raise ValueError("Name can only contain alphanumeric characters")
        return name

    def to_dict(self) -> dict:
        return {"name": self._name}

    def __eq__(self, __value: object) -> bool:
        return self._name == __value._name
