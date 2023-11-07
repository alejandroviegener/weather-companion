"""
Repository for location bookmarks for users
"""

from typing import List, Tuple

from weather_companion.weather_journal import AuthorID, Bookmark
from weather_companion.weather_station import Location

from .errors import RepositoryError


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
