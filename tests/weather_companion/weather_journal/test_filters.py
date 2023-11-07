from datetime import datetime, timedelta
from typing import List

import pytest

from weather_companion.weather_journal import AuthorID, JournalEntry, Note
from weather_companion.weather_journal.filters import (
    AndFilter,
    DateRangeFilter,
    LocationProximityFilter,
    NoteContentFilter,
)
from weather_companion.weather_station import Location

now = datetime.now()


# Create journal to use in tests
@pytest.fixture
def journal() -> List[JournalEntry]:
    note_1 = Note(content="Test content 1")
    note_2 = Note(content="Test content 2")
    note_3 = Note(content="Test content 3")

    location_1 = Location(
        latitude=10.223,
        longitude=23.345,
    )

    location_2 = Location(
        latitude=14.223,
        longitude=21.345,
    )

    location_3 = Location(
        latitude=54.223,
        longitude=26.345,
    )

    new_entry_1 = JournalEntry(location=location_1, note=note_1, date=now)
    new_entry_2 = JournalEntry(location=location_2, note=note_2, date=now + timedelta(days=1))
    new_entry_3 = JournalEntry(location=location_3, note=note_3, date=now + timedelta(days=2))

    return [new_entry_1, new_entry_2, new_entry_3]


def test_should_return_fitered_entries_by_date_range(journal):
    start_date = now
    end_date = now + timedelta(days=1)

    filter_by_date_range = DateRangeFilter(start_date, end_date)
    filtered_entries = list(filter(filter_by_date_range.condition, journal))
    assert len(filtered_entries) == 2
    assert filtered_entries[0].date() == start_date
    assert filtered_entries[1].date() == end_date


def test_should_return_filtered_entries_by_note_content(journal):
    filter_by_content = NoteContentFilter("Test content 2")
    filtered_entries = list(filter(filter_by_content.condition, journal))
    assert len(filtered_entries) == 1
    assert filtered_entries[0].note().content() == "Test content 2"


def test_should_return_filtered_entries_of_and_filter(journal):
    location = Location(
        latitude=10.223,
        longitude=23.345,
    )

    start_date = now
    end_date = now + timedelta(days=1)

    location = Location(
        latitude=10.223,
        longitude=23.345,
    )

    filter_by_location_proximity = LocationProximityFilter(location, 1000)
    filter_by_date_range = DateRangeFilter(start_date, end_date)

    and_filter = AndFilter([filter_by_location_proximity, filter_by_date_range])
    filtered_entries = list(filter(and_filter.condition, journal))
    assert len(filtered_entries) == 2
    assert filtered_entries[0].location() == location
    assert filtered_entries[0].date() == start_date


def test_should_return_filtered_entries_by_location_proximity(journal):
    location = Location(
        latitude=10.223,
        longitude=23.345,
    )

    filter_by_location_proximity = LocationProximityFilter(location, 1000)
    filtered_entries = list(filter(filter_by_location_proximity.condition, journal))
    assert len(filtered_entries) == 2
