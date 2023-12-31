import os
from datetime import date, timedelta

import pytest

from weather_companion.weather_station import (
    ClientError,
    Location,
    OWMClient,
    OWMWeatherStation,
    WeatherStationError,
)


class OpenWeatherMapClientMock(OWMClient):
    """
    Mocks the OpenWeatherMapClient class. Used to test the OpenWeatherMap class.
    """

    def __init__(self) -> None:
        self._current_state_response = None
        self._error = None

    def set_current_state_response(self, response: dict, error: Exception = None) -> None:
        self._current_state_response = response
        self._error = error

    def get_current_state(self, location: Location) -> dict:
        if self._error:
            raise self._error
        return self._current_state_response


def test_get_current_state_response_should_include_mandatory_data():
    client = OpenWeatherMapClientMock()
    weather_station = OWMWeatherStation(client=client)

    complete_data = {
        "temp": 23,
        "humidity": 40,
        "feels_like": 21,
        "pressure": 1042,
    }
    client.set_current_state_response({"main": complete_data})

    location = Location(51.5074, 0.1278)
    weather_state = weather_station.get_current_state(location)
    assert weather_state.temperature == 23
    assert weather_state.humidity == 40
    assert weather_state.feels_like == 21
    assert weather_state.pressure == 1042


def test_get_current_state_response_should_include_all_optional_data_if_present():
    client = OpenWeatherMapClientMock()
    weather_station = OWMWeatherStation(client=client)
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
    weather_state = weather_station.get_current_state(Location(51.5074, 0.1278))
    assert weather_state.temperature == 23
    assert weather_state.humidity == 40
    assert weather_state.feels_like == 21
    assert weather_state.pressure == 1042
    assert weather_state.clouds == 20
    assert weather_state.rain_1h == 0.5
    assert weather_state.rain_3h == 1.5
    assert weather_state.snow_1h == 0.5
    assert weather_state.snow_3h == 1.5
    assert weather_state.wind_speed == 10
    assert weather_state.wind_gust == 15
    assert weather_state.wind_direction == 180


def test_get_current_state_should_fail_if_unexpected_weather_data_format_in_client():
    """
    Test that the weather station fails if the client does not return main weather data.
    """
    client = OpenWeatherMapClientMock()
    weather_station = OWMWeatherStation(client=client)

    client.set_current_state_response({"main": {}})
    location = Location(51.5074, 0.1278)
    with pytest.raises(WeatherStationError) as e:
        weather_station.get_current_state(location)

    client.set_current_state_response({})
    location = Location(51.5074, 0.1278)
    with pytest.raises(WeatherStationError):
        weather_station.get_current_state(location)


def test_get_current_state_should_fail_if_error_raised_by_client():
    client = OpenWeatherMapClientMock()
    weather_station = OWMWeatherStation(client=client)

    client.set_current_state_response(None, ClientError("some error message"))
    location = Location(51.5074, 0.1278)
    with pytest.raises(WeatherStationError) as e:
        weather_station.get_current_state(location)
    assert str(e.value).startswith("Client error:")


def test_get_current_state_should_fail_if_mandatory_data_missing():
    client = OpenWeatherMapClientMock()
    weather_station = OWMWeatherStation(client=client)

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
        location = Location(51.5074, 0.1278)
        with pytest.raises(WeatherStationError) as e:
            weather_station.get_current_state(location)


def _test_get_forecast_should_include_mandatory_data():
    # read api key from env variable
    api_key = os.environ.get("OPEN_WEATHER_MAP_API_KEY", None)
    client = OWMClient(api_key=api_key)
    weather_station = OWMWeatherStation(client=client)

    location = Location(-34.6037, -58.3816, "SanNicolas")
    forecast = weather_station.get_forecast(
        location=location,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
    )

    print([str(d) for d in forecast.get_dates()])
    print(forecast.get_weather_states_for_date(date.today()))
    raise Exception("test not implemented")
