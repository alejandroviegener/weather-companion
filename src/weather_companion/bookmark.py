from .weather_station import Location


class LocationBookmark:
    """Class to represent a bookmarked location.
    A location bookmark is a Location with an associated name.
    """

    def __init__(self, name: str, location: Location):
        self._check_valid_name(name)
        self._name = name
        self._location = location

    def name(self) -> str:
        return self._name

    def location(self) -> Location:
        return self._location

    def _check_valid_name(self, name):
        if not name:
            raise ValueError("Name can not be blank")
        if " " in name:
            raise ValueError("Name can not contain spaces")
        if not name.isalnum():
            raise ValueError("Name can only contain alphanumeric characters")
