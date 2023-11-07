"""
Test WeatherJournal class
"""

from datetime import datetime, timedelta

import pytest

from weather_companion.weather_journal import (
    AuthorID,
    JournalEntry,
    Note,
    WeatherJournal,
)
from weather_companion.weather_station import Location


# Create empty journal to use in tests
@pytest.fixture
def journal():
    author = AuthorID(id="user@test.com")
    journal = WeatherJournal(author=author)
    return journal


def test_new_journal_is_empty(journal):
    assert len(journal) == 0


def test_add_journal_entry_in_empty_journal(journal):
    note = Note(content="Test content")
    location = Location(label="TestLocation", latitude=10.223, longitude=23.345)
    new_entry = JournalEntry(location=location, date=datetime.now(), note=note)

    assert len(journal) == 0
    journal.add_entry(new_entry)
    assert len(journal) == 1
    assert new_entry == list(journal)[0]


def test_add_journal_entry_in_journal_with_entries(journal):
    note_1 = Note(content="Test content 1")
    note_2 = Note(content="Test content 2")
    location = Location(label="TestLocation", latitude=10.223, longitude=23.345)
    new_entry_1 = JournalEntry(location=location, date=datetime.now(), note=note_1)
    new_entry_2 = JournalEntry(location=location, date=datetime.now(), note=note_2)
    journal.add_entry(new_entry_1)

    assert len(journal) == 1
    journal.add_entry(new_entry_2)
    assert len(journal) == 2

    assert new_entry_1 in list(journal)
    assert new_entry_2 in list(journal)


def test_belong_to_author(journal):
    true_author = AuthorID(id="test@user.com")
    false_author = AuthorID(id="bla@bla.com")
    journal = WeatherJournal(author=true_author)
    assert journal.belongs_to(true_author) == True
    assert journal.belongs_to(false_author) == False


def test_iterator_is_ordered_by_date(journal):
    note_1 = Note(content="Test content 1")
    note_2 = Note(content="Test content 2")
    location = Location(label="TestLocation", latitude=10.223, longitude=23.345)
    new_entry_1 = JournalEntry(location=location, date=datetime.now(), note=note_1)
    new_entry_2 = JournalEntry(location=location, date=datetime.now() + timedelta(seconds=1), note=note_2)
    journal.add_entry(new_entry_2)
    journal.add_entry(new_entry_1)

    assert list(journal)[0] == new_entry_1
    assert list(journal)[1] == new_entry_2
