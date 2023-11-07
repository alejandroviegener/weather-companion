from datetime import datetime
from typing import Iterable, List

from weather_companion.weather_station import Location

from .weather_journal import JournalEntry


class JournalEntryFilter:
    """
    Interface for a journal entry filter:
        - receives journal entry and returns true if it should be included in the result
    """

    def condition(self, journal_entrie: JournalEntry) -> bool:
        raise NotImplementedError("filter method not implemented")


# Filters weather journal entries by date range
class DateRangeFilter(JournalEntryFilter):
    def __init__(self, start_date: datetime, end_date: datetime):
        self._start_date = start_date
        self._end_date = end_date

    def condition(self, journal_entry: JournalEntry) -> bool:
        return self._start_date <= journal_entry.date() <= self._end_date


# Filters weather journal entries by note content
class NoteContentFilter(JournalEntryFilter):
    def __init__(self, content: str):
        self._content = content

    def condition(self, journal_entry: JournalEntry) -> bool:
        searched_content = self._content.lower().strip()
        return searched_content in journal_entry.note().content().lower()


# Filters weather entry journals by location proximity (in km)
class LocationProximityFilter(JournalEntryFilter):
    def __init__(self, location: Location, max_distance: float):
        self._location = location
        self._max_distance = max_distance

    def condition(self, journal_entry: JournalEntry) -> bool:
        return self._location.distance_to(journal_entry.location()) <= self._max_distance


# And filter that combines multiple filters
class AndFilter(JournalEntryFilter):
    def __init__(self, filters: Iterable[JournalEntryFilter]):
        self._filters = filters

    def condition(self, journal_entry: JournalEntry) -> bool:
        return all([filter.condition(journal_entry) for filter in self._filters])
