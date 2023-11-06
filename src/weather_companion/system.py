from datetime import date

from .bookmark import LocationBookmark
from .weather_journal import AuthorID, WeatherJournal
from .weather_station import (
    Forecast,
    Location,
    WeatherState,
    WeatherStation,
    WeatherStationError,
)


class WeatherCompanionError(Exception):
    """
    Defines an exception that is raised when an error occurs in the WeatherCompanion class.
    """

    def __init__(self, message):
        """
        Creates a new instance of the WeatherCompanionError class.
        """
        super().__init__(message)


class WeatherCompanion:
    def __init__(self, weather_station: WeatherStation):
        self._weather_station = weather_station

    def get_current_state(self, location: Location) -> WeatherState:
        """
        Gets the current weather state for a given location.
        Throws WeatherCompanionError if the weather station is unable to provide the weather state.
        """
        try:
            weather_state = self._weather_station.get_current_state(location)
        except WeatherStationError as ex:
            raise WeatherCompanionError("Unable to get current weather state") from ex
        return weather_state

    def get_forecast(
        self, location: Location, start_date: date, end_date: date
    ) -> Forecast:
        """
        Gets the weather forecast for a given location for a given date range
        Throws WeatherCompanionError if the weather station is unable to provide the weather forecast.
        """
        try:
            forecast = self._weather_station.get_forecast(
                location, start_date, end_date
            )
        except WeatherStationError as ex:
            raise WeatherCompanionError("Unable to get weather forecast") from ex
        return forecast

    # Add a new weather journal entry for an author into the repository
    def add_journal_entry(self, journal_entry: WeatherJournal, author: AuthorID):
        pass

    # Remove a weather journal entry for an author from the repository
    def remove_journal_entry(self, journal_entry: WeatherJournal, author: AuthorID):
        pass

    # Update a weather journal entry for an author from the repository
    def update_journal_entry(self, journal_entry: WeatherJournal, author: AuthorID):
        pass

    # Get all weather journal entries for an author from the repository
    def get_journal_entries(self, author: AuthorID) -> WeatherJournal:
        pass

    # Get bookmarks for an author from the repository
    def get_bookmarks(self, author: AuthorID):
        pass

    # Add a new bookmark for an author into the repository
    def add_bookmark(self, bookmark: LocationBookmark, author: AuthorID):
        pass

    # Remove a bookmark for an author from the repository
    def remove_bookmark(self, bookmark: LocationBookmark, author: AuthorID):
        pass

    # Update a bookmark for an author from the repository
    def update_bookmark(self, bookmark: LocationBookmark, author: AuthorID):
        pass

    # Get the weather state for a bookmark
    def get_bookmark_weather(self, bookmark: LocationBookmark) -> WeatherState:
        pass
