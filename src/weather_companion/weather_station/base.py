from datetime import date

from .location import Location


class WeatherStationError(Exception):
    """
    Defines an exception that is raised when an error occurs in the WeatherStation class.
    """

    def __init__(self, message):
        """
        Creates a new instance of the WeatherStationError class.
        """
        super().__init__(message)


class WeatherStation:
    """
    Defines an interface for weather forecast providers.
    """

    def get_current_state(self, location: Location):
        """
        Gets the current weather state for a given location.
        """
        raise NotImplementedError

    def get_forecast(self, location: Location, start_date: date, end_date: date):
        """
        Gets the weather forecast for a given location for a given date range
        """
        raise NotImplementedError
