from datetime import date

from weather_companion.bookmark import LocationBookmark
from weather_companion.repository import JournalRepository, RepositoryError
from weather_companion.weather_journal import AuthorID, JournalEntry, WeatherJournal
from weather_companion.weather_station import (
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
    def __init__(
        self, weather_station: WeatherStation, journal_repository: JournalRepository
    ):
        self._weather_station = weather_station
        self._journal_repository = journal_repository

    #########################################################################################################
    ####################################### WeatherStation ##################################################
    #########################################################################################################

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

    #########################################################################################################
    ############################################ Journal ####################################################
    #########################################################################################################

    def add_journal_entry(self, journal_entry: WeatherJournal, author: AuthorID) -> int:
        """
        Adds a new weather journal entry for an author into the repository
        Throws WeatherCompanionError if the journal entry cannot be added
        """
        try:
            id = self._journal_repository.add(journal_entry, author)
        except RepositoryError as ex:
            raise WeatherCompanionError("Unable to add journal entry") from ex
        return id

    def get_journal_entry(
        self, journal_entry_id: int, author: AuthorID
    ) -> JournalEntry:
        """
        Gets a weather journal entry for an author from the repository
        Throws WeatherCompanionError if the journal entry cannot be found
        """
        try:
            entry = self._journal_repository.get(journal_entry_id, author)
        except RepositoryError as ex:
            raise WeatherCompanionError("Unable to get journal entry") from ex
        return entry

    # Remove a weather journal entry for an author
    def remove_journal_entry(self, journal_entry_id: int, author: AuthorID):
        """
        Removes a weather journal entry for an author from the repository
        Throws WeatherCompanionError if the journal entry cannot be removed
        """
        try:
            self._journal_repository.remove(journal_entry_id, author)
        except RepositoryError as ex:
            raise WeatherCompanionError("Unable to remove journal entry") from ex

    def update_journal_entry(
        self, journal_entry_id: int, author: AuthorID, new_journal_entry: JournalEntry
    ):
        """
        Updates a weather journal entry for an author into the repository
        Throws WeatherCompanionError if the journal entry cannot be updated
        """
        try:
            self._journal_repository.update(journal_entry_id, author, new_journal_entry)
        except RepositoryError as ex:
            raise WeatherCompanionError("Unable to update journal entry") from ex

    def get_all_journal_entries(self, author: AuthorID) -> WeatherJournal:
        """
        Gets the weather journal for an author
        """
        try:
            journal = self._journal_repository.get_all_entries(author)
        except RepositoryError as ex:
            raise WeatherCompanionError("Unable to get journal") from ex
        return journal

    #########################################################################################################
    ########################################### Bookmarks ###################################################
    #########################################################################################################

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
