import pytest

from weather_companion.weather_station import (
    Location,
    OpenWeatherMap,
    OpenWeatherMapClient,
    WeatherStationError,
)


class OpenWeatherMapClientMock(OpenWeatherMapClient):
    """
    Mocks the OpenWeatherMapClient class. Used to test the OpenWeatherMap class.
    """

    def __init__(self) -> None:
        self._current_state_response = None

    def set_current_state_response(self, response: dict):
        self._current_state_response = response

    def current_state(self, location: Location) -> dict:
        return self._current_state_response


def test_response_should_include_mandatory_data():
    client = OpenWeatherMapClientMock()
    weather_station = OpenWeatherMap(client=client)

    complete_data = {
        "temp": 23,
        "humidity": 40,
        "feels_like": 21,
        "pressure": 1042,
    }
    client.set_current_state_response({"main": complete_data})

    location = Location(51.5074, 0.1278, "London")
    response = weather_station.current_state(location)
    expected_response = {
        "temperature": 23,
        "humidity": 40,
        "feels_like": 21,
        "pressure": 1042,
    }
    assert response == expected_response


def test_response_should_include_all_optional_data_if_present():
    client = OpenWeatherMapClientMock()
    weather_station = OpenWeatherMap(client=client)
    complete_mandatory_and_optional_data = {
        "main": {
            "temp": 23,
            "humidity": 40,
            "feels_like": 21,
            "pressure": 1042,
        },
        "wind": {"speed": 10, "gust": 15, "deg": 180},
        "clouds": {"all": 20},
        "rain": {
            "1h": 0.5,
            "3h": 1.5,
            "4h": 2.5,  # This should be ignored
        },
        "snow": {
            "1h": 0.5,
            "3h": 1.5,
            "4h": 2.5,  # This should be ignored
        },
    }
    client.set_current_state_response(complete_mandatory_and_optional_data)
    response = weather_station.current_state(Location(51.5074, 0.1278, "London"))
    expected_response = {
        "temperature": 23,
        "humidity": 40,
        "feels_like": 21,
        "pressure": 1042,
        "wind_speed": 10,
        "wind_gust": 15,
        "wind_direction": 180,
        "clouds": 20,
        "rain_1h": 0.5,
        "rain_3h": 1.5,
        "snow_1h": 0.5,
        "snow_3h": 1.5,
    }
    assert response == expected_response


def test_should_fail_if_no_main_weather_data_in_client():
    """
    Test that the weather station fails if the client does not return main weather data.
    """
    client = OpenWeatherMapClientMock()
    weather_station = OpenWeatherMap(client=client)

    client.set_current_state_response({"main": None})
    location = Location(51.5074, 0.1278, "London")
    with pytest.raises(WeatherStationError):
        weather_station.current_state(location)

    client.set_current_state_response({})
    location = Location(51.5074, 0.1278, "London")
    with pytest.raises(WeatherStationError):
        weather_station.current_state(location)


def test_should_fail_if_mandatory_data_missing():
    client = OpenWeatherMapClientMock()
    weather_station = OpenWeatherMap(client=client)

    complete_data = {
        "temp": 23,
        "humidity": 40,
        "feels_like": 21,
        "pressure": 1042,
    }
    for field in complete_data.keys():
        incomplete_data = complete_data.copy()
        del incomplete_data[field]
        client.set_current_state_response({"main": incomplete_data})
        location = Location(51.5074, 0.1278, "London")
        with pytest.raises(WeatherStationError):
            weather_station.current_state(location)
