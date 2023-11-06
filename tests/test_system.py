from datetime import date

import pytest

from weather_companion import system
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
    weather_companion = system.WeatherCompanion(weather_station)
    location = Location(latitude=10, longitude=20, label="test")
    result = weather_companion.get_current_state(location)
    assert result == state


def test_should_raise_exception_if_error_getting_current_weather_state():
    weather_station = WeatherStationMock()
    weather_station.exception = WeatherStationError("test")
    weather_companion = system.WeatherCompanion(weather_station)
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
    weather_companion = system.WeatherCompanion(weather_station)

    location = Location(latitude=10, longitude=20, label="test")
    result = weather_companion.get_forecast(
        location, start_date="2020-01-01", end_date="2020-01-02"
    )
    assert result == forecast


def test_should_raise_exception_if_error_getting_forecast():
    weather_station = WeatherStationMock()
    weather_station.exception = WeatherStationError("test")
    weather_companion = system.WeatherCompanion(weather_station)
    location = Location(latitude=10, longitude=20, label="test")

    with pytest.raises(system.WeatherCompanionError):
        weather_companion.get_forecast(
            location, start_date="2020-01-01", end_date="2020-01-02"
        )
