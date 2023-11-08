from datetime import datetime
from typing import List

from weather_companion.weather_station.location import Location

from .author import AuthorID
from .note import Note


class JournalEntry:
    def __init__(self, location: Location, date: datetime, note: Note):
        self._location = location
        self._date = date
        self._note = note

    def location(self) -> Location:
        return self._location

    def date(self) -> datetime:
        return self._date

    def note(self) -> Note:
        return self._note

    def __str__(self):
        return f"{self._location.name()} - {self._date} - {self._note}"

    def __eq__(self, __value: object) -> bool:
        return self._location == __value._location and self._date == __value._date and self._note == __value._note


class ___WeatherJournal___:
    """
    A weather journal is a collection of journal entries
    """

    def __init__(self, author: AuthorID):
        self._author = author
        self._journal_entries = []

    # @TODO remove this, move to initializer, and make class immutable
    def add_entry(self, entry: JournalEntry):
        self._journal_entries.append(entry)

    def belongs_to(self, author: AuthorID) -> bool:
        return self._author == author

    def __len__(self):
        return len(self._journal_entries)

    def __iter__(self):
        """Returns an iterator over the journal entries sorted by date"""
        return iter(sorted(self._journal_entries, key=lambda entry: entry.date()))
