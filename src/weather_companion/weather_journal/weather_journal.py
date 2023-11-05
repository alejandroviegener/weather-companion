from datetime import datetime
from typing import Iterable

from weather_companion.weather_station.location import Location


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


class Note:
    MAX_LENGTH = 1000

    def __init__(self, content: str):
        """
        Create a Note, content must be:
          - a non empty string
          - alphanumeric only
          - less than 1000 characters
        """
        self._content = self._validate_content(content)

    def _validate_content(self, content: str) -> str:
        """
        check if content is valid: less than 1000 characters, alphanumeric only
        """
        content = content.strip()
        if not content:
            raise ValueError("The content cannot be empty.")
        if len(content) > Note.MAX_LENGTH:
            raise ValueError("The content cannot be longer than 1000 characters.")

        return content

    def __eq__(self, __value: object) -> bool:
        return self._content == __value._content


class JournalEntry:
    def __init__(self, location: Location, date: datetime, note: Note):
        self._location = location
        self._date = date
        self._note = note

    def location(self):
        return self._location

    def date(self):
        return self._date

    def note(self):
        return self._note

    def __str__(self):
        return f"{self._location.name()} - {self._date} - {self._note}"

    def __eq__(self, __value: object) -> bool:
        return (
            self._location == __value._location
            and self._date == __value._date
            and self._note == __value._note
        )


class JournalEntryFilter:
    """
    Interface fora journal entry filter:
        - receives an iterable of journal entries
        - returns an iterable of journal entries
    """

    def filter(self, journal_entries: Iterable[JournalEntry]) -> Iterable[JournalEntry]:
        raise NotImplementedError("filter method not implemented")


class WeatherJournal:
    """
    A weather journal is a collection of journal entries
    """

    def __init__(self, author: AuthorID):
        self._author = author
        self._journal_entries = []

    def add_entry(self, entry: JournalEntry):
        self._journal_entries.append(entry)

    def get_entries(self, filter: JournalEntryFilter = None) -> Iterable[JournalEntry]:
        if filter is None:
            return self._journal_entries
        return filter.filter(self._journal_entries)

    def belongs_to(self, author: AuthorID) -> bool:
        return self._author == author

    def __len__(self):
        return len(self._journal_entries)
