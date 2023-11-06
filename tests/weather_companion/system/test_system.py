from datetime import date

import pytest

from weather_companion import system
from weather_companion.repository import InMemoryJournalRepository
from weather_companion.weather_journal import (
    AuthorID,
    JournalEntry,
    Note,
    WeatherJournal,
)
from weather_companion.weather_station import (
    Forecast,
    Location,
    WeatherState,
    WeatherStation,
    WeatherStationError,
)


class WeatherStationMock(WeatherStation):
    def __init__(self):
        self.weather_state = None
        self.exception = None
        self.forecast = None

    def get_current_state(self, location: Location) -> WeatherState:
        if self.exception:
            raise self.exception
        return self.weather_state

    def get_forecast(
        self, location: Location, start_date: date, end_date: date
    ) -> Forecast:
        if self.exception:
            raise self.exception
        return self.forecast


def test_should_get_current_weather_state():
    weather_station = WeatherStationMock()
    state = WeatherState(
        temperature=10,
        humidity=20,
        wind_speed=30,
        wind_direction=40,
        feels_like=11,
        pressure=1024,
    )
    weather_station.weather_state = state
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=None
    )
    location = Location(latitude=10, longitude=20, label="test")
    result = weather_companion.get_current_state(location)
    assert result == state


def test_should_raise_exception_if_error_getting_current_weather_state():
    weather_station = WeatherStationMock()
    weather_station.exception = WeatherStationError("test")
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=None
    )
    location = Location(latitude=10, longitude=20, label="test")

    with pytest.raises(system.WeatherCompanionError):
        weather_companion.get_current_state(location)


def test_should_get_forecast():
    forecast = Forecast()
    weather_state = WeatherState(
        temperature=10,
        humidity=20,
        wind_speed=30,
        wind_direction=40,
        feels_like=11,
        pressure=1024,
    )
    forecast.add(weather_state, date_time="2020-01-01")

    weather_station = WeatherStationMock()
    weather_station.forecast = forecast
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=None
    )

    location = Location(latitude=10, longitude=20, label="test")
    result = weather_companion.get_forecast(
        location, start_date="2020-01-01", end_date="2020-01-02"
    )
    assert result == forecast


def test_should_raise_exception_if_error_getting_forecast():
    weather_station = WeatherStationMock()
    weather_station.exception = WeatherStationError("test")
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=None
    )
    location = Location(latitude=10, longitude=20, label="test")

    with pytest.raises(system.WeatherCompanionError):
        weather_companion.get_forecast(
            location, start_date="2020-01-01", end_date="2020-01-02"
        )


def test_should_add_journal_entry():
    weather_station = WeatherStationMock()
    journal_repository = InMemoryJournalRepository()
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=journal_repository
    )
    journal_entry = JournalEntry(
        location=Location(latitude=10, longitude=20, label="test"),
        date="2020-01-01",
        note=Note("test note"),
    )
    author = AuthorID("test")
    result = weather_companion.add_journal_entry(journal_entry, author)
    assert result == 0


def test_should_get_journal_entry():
    weather_station = WeatherStationMock()
    journal_repository = InMemoryJournalRepository()
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=journal_repository
    )
    journal_entry = JournalEntry(
        location=Location(latitude=10, longitude=20, label="test"),
        date="2020-01-01",
        note=Note("test note"),
    )
    author = AuthorID("test")
    id = weather_companion.add_journal_entry(journal_entry, author)
    result = weather_companion.get_journal_entry(id, author)
    assert result == journal_entry


def test_should_remove_existing_journal_entry():
    weather_station = WeatherStationMock()
    journal_repository = InMemoryJournalRepository()
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=journal_repository
    )
    journal_entry = JournalEntry(
        location=Location(latitude=10, longitude=20, label="test"),
        date="2020-01-01",
        note=Note("test note"),
    )
    author = AuthorID("test")
    id = weather_companion.add_journal_entry(journal_entry, author)
    weather_companion.remove_journal_entry(id, author)
    with pytest.raises(system.WeatherCompanionError):
        weather_companion.get_journal_entry(id, author)


def test_should_update_existing_journal_entry():
    weather_station = WeatherStationMock()
    journal_repository = InMemoryJournalRepository()
    weather_companion = system.WeatherCompanion(
        weather_station=weather_station, journal_repository=journal_repository
    )
    journal_entry = JournalEntry(
        location=Location(latitude=10, longitude=20, label="test"),
        date="2020-01-01",
        note=Note("test note"),
    )
    author = AuthorID("test")
    id = weather_companion.add_journal_entry(journal_entry, author)
    new_journal_entry = JournalEntry(
        location=Location(latitude=10, longitude=20, label="test"),
        date="2020-01-01",
        note=Note("test note 2"),
    )
    weather_companion.update_journal_entry(id, author, new_journal_entry)
    result = weather_companion.get_journal_entry(id, author)
    assert result == new_journal_entry
