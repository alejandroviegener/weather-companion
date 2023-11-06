from datetime import datetime
from typing import Iterable, List

from weather_companion.weather_station import Location

from .weather_journal import JournalEntry


class JournalEntryFilter:
    """
    Interface fora journal entry filter:
        - receives an iterable of journal entries
        - returns an iterable of journal entries
    """

    def filter(self, journal_entries: Iterable[JournalEntry]) -> List[JournalEntry]:
        raise NotImplementedError("filter method not implemented")


# Filters weather journal entries by exact location
class LocationFilter(JournalEntryFilter):
    def __init__(self, location: Location):
        self._location = location

    def filter(self, journal_entries: Iterable[JournalEntry]) -> List[JournalEntry]:
        return [
            entry for entry in journal_entries if entry.location() == self._location
        ]


# Filters weather journal entries by date range
class DateRangeFilter(JournalEntryFilter):
    def __init__(self, start_date: datetime, end_date: datetime):
        self._start_date = start_date
        self._end_date = end_date

    def filter(self, journal_entries: Iterable[JournalEntry]) -> List[JournalEntry]:
        return [
            entry
            for entry in journal_entries
            if self._start_date <= entry.date() <= self._end_date
        ]


# Filters weather journal entries by note content
class NoteContentFilter(JournalEntryFilter):
    def __init__(self, content: str):
        self._content = content

    def filter(self, journal_entries: Iterable[JournalEntry]) -> List[JournalEntry]:
        searched_content = self._content.lower()
        return [
            entry
            for entry in journal_entries
            if searched_content in entry.note().content().lower()
        ]


# Filters weather entry journals by location proximity (in km)
class LocationProximityFilter(JournalEntryFilter):
    def __init__(self, location: Location, max_distance: float):
        self._location = location
        self._max_distance = max_distance

    def filter(self, journal_entries: Iterable[JournalEntry]) -> List[JournalEntry]:
        return [
            entry
            for entry in journal_entries
            if self._location.distance_to(entry.location()) <= self._max_distance
        ]


# And filter that combines multiple filters
class AndFilter(JournalEntryFilter):
    def __init__(self, filters: Iterable[JournalEntryFilter]):
        self._filters = filters

    def filter(self, journal_entries: Iterable[JournalEntry]) -> List[JournalEntry]:
        filtered_entries = list(journal_entries)
        for filter in self._filters:
            filtered_entries = filter.filter(filtered_entries)
        return filtered_entries
