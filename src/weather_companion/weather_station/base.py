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

    def current_state(self, location: Location):
        """
        Gets the current weather state for a given location.
        """
        raise NotImplementedError

    def forecast(self, latitude, longitude, date_time):
        """
        Gets the weather forecast for a given latitude and longitude for a given date and time.
        """
        raise NotImplementedError
