"""
Repository for location bookmarks for users
"""

from typing import List, Tuple

from weather_companion.weather_journal import AuthorID
from weather_companion.weather_station import Location

from .errors import RepositoryError


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


class LocationBookmarkRepository:
    def add(self, bookmark: Bookmark, location: Location, author_id: AuthorID) -> None:
        pass

    def get(self, bookmark: Bookmark, author_id: AuthorID) -> Location:
        pass

    def remove(self, bookmark: Bookmark, author_id: AuthorID) -> None:
        pass

    def get_all_bookmarks(self, author_id: AuthorID) -> List[Tuple[Bookmark, Location]]:
        pass


class InMemoryLocationBookmarkRepository:
    def __init__(self):
        self._container = []

    def add(self, bookmark: Bookmark, location: Location, author_id: AuthorID) -> None:
        """
        Adds the bookmark to the container
        check if already exists
        """
        for entry in self._container:
            if entry[0] == bookmark and entry[2] == author_id:
                raise RepositoryError("Bookmark already exists")
        self._container.append([bookmark, location, author_id])

    def get(self, bookmark: Bookmark, author_id: AuthorID) -> Location:
        """
        Gets the bookmark from the container
        """
        for entry in self._container:
            if entry[0] == bookmark and entry[2] == author_id:
                return entry[1]
        raise RepositoryError("Bookmark not found")

    def remove(self, bookmark: Bookmark, author_id: AuthorID) -> None:
        """
        Removes the bookmark from the container
        """
        for entry in self._container:
            if entry[0] == bookmark and entry[2] == author_id:
                self._container.remove(entry)
                return  # Exit
        raise RepositoryError("Bookmark not found")

    def get_all_bookmarks(self, author_id: AuthorID) -> List[Tuple[Bookmark, Location]]:
        """
        Gets all bookmarks for an author
        """
        return [(entry[0], entry[1]) for entry in self._container if entry[2] == author_id]
