from datetime import date

from .forecast import Forecast
from .location import Location
from .weather_state import WeatherState


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

    def get_current_state(self, location: Location) -> WeatherState:
        """
        Gets the current weather state for a given location.
        Throws WeatherStationError if the weather station is unable to provide the weather state.
        """
        raise NotImplementedError

    def get_forecast(self, location: Location, start_date: date, end_date: date) -> Forecast:
        """
        Gets the weather forecast for a given location for a given date range
        Throws WeatherStationError if the weather station is unable to provide the weather forecast.
        """
        raise NotImplementedError
