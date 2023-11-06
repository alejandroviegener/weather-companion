from datetime import datetime, timedelta

import pytest

from weather_companion.weather_journal import (
    AuthorID,
    JournalEntry,
    Note,
    WeatherJournal,
)
from weather_companion.weather_journal.filters import (
    AndFilter,
    DateRangeFilter,
    LocationFilter,
    LocationProximityFilter,
    NoteContentFilter,
)
from weather_companion.weather_station import Location

now = datetime.now()


# Create journal to use in tests
@pytest.fixture
def journal():
    author = AuthorID(id="user@test.com")
    journal = WeatherJournal(author=author)

    note_1 = Note(content="Test content 1")
    note_2 = Note(content="Test content 2")
    note_3 = Note(content="Test content 3")

    location_1 = Location(
        label="TestLocation1",
        latitude=10.223,
        longitude=23.345,
    )

    location_2 = Location(
        label="TestLocation2",
        latitude=14.223,
        longitude=21.345,
    )

    location_3 = Location(
        label="TestLocation3",
        latitude=54.223,
        longitude=26.345,
    )

    new_entry_1 = JournalEntry(location=location_1, note=note_1, date=now)
    new_entry_2 = JournalEntry(
        location=location_2, note=note_2, date=now + timedelta(days=1)
    )
    new_entry_3 = JournalEntry(
        location=location_3, note=note_3, date=now + timedelta(days=2)
    )

    journal.add_entry(new_entry_1)
    journal.add_entry(new_entry_2)
    journal.add_entry(new_entry_3)
    return journal


def test_should_return_filtered_entries_by_location(journal):
    location = Location(
        label="TestLocation1",
        latitude=10.223,
        longitude=23.345,
    )

    filter_by_location = LocationFilter(location)
    filtered_entries = filter_by_location.filter(journal)
    assert len(filtered_entries) == 1
    assert filtered_entries[0].location() == location


def test_should_return_fitered_entries_by_date_range(journal):
    start_date = now
    end_date = now + timedelta(days=1)

    filter_by_date_range = DateRangeFilter(start_date, end_date)
    filtered_entries = filter_by_date_range.filter(journal)
    assert len(filtered_entries) == 2
    assert filtered_entries[0].date() == start_date
    assert filtered_entries[1].date() == end_date


def test_should_return_filtered_entries_by_note_content(journal):
    filter_by_content = NoteContentFilter("Test content 2")
    filtered_entries = filter_by_content.filter(journal)
    assert len(filtered_entries) == 1
    assert filtered_entries[0].note().content() == "Test content 2"


def test_should_return_filtered_entries_of_and_filter(journal):
    location = Location(
        label="TestLocation1",
        latitude=10.223,
        longitude=23.345,
    )

    start_date = now
    end_date = now + timedelta(days=1)

    filter_by_location = LocationFilter(location)
    filter_by_date_range = DateRangeFilter(start_date, end_date)

    and_filter = AndFilter([filter_by_location, filter_by_date_range])
    filtered_entries = and_filter.filter(journal)
    assert len(filtered_entries) == 1
    assert filtered_entries[0].location() == location
    assert filtered_entries[0].date() == start_date


def test_should_return_filtered_entries_by_location_proximity(journal):
    location = Location(
        label="TestLocation1",
        latitude=10.223,
        longitude=23.345,
    )

    filter_by_location_proximity = LocationProximityFilter(location, 1000)
    filtered_entries = filter_by_location_proximity.filter(journal)
    assert len(filtered_entries) == 2
