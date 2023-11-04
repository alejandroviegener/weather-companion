from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Tuple

from .forecast import Forecast
from .owm_client import ClientError, OWMClient
from .weather_state import WeatherState, WeatherStateBuilder
from .weather_station import Location, WeatherStationError


class OWMWeatherStation:
    """
    Defines a weather forecast provider that uses OpenWeatherMap.
    """

    def __init__(self, client: OWMClient):
        """
        Creates a new instance of the OpenWeatherMap class.
        """
        self._client = client

    def get_current_state(self, location) -> WeatherState:
        """
        Gets the current weather state for a given location.
        """
        try:
            client_data = self._client.get_current_state(location)
        except ClientError as ex:
            raise WeatherStationError(f"Client error: {ex}")

        weather_state = self._build_weather_state(client_data)
        return weather_state

    def get_forecast(
        self, location: Location, start_date: date, end_date: date
    ) -> Forecast:
        """
        Gets the weather forecast for a given latitude and longitude for a given date and time.
        """
        try:
            client_data = self._client.get_forecast(location)
        except ClientError as ex:
            raise WeatherStationError(f"Client error: {ex}")

        forecast = self._build_forecast(client_data, start_date, end_date)
        return forecast

    def _build_forecast(self, client_data: Dict, start_date: date, end_date: date):
        location_timezone = self._get_timezone(client_data)
        forecast_data = self._get_forecast_data(client_data)

        # Get weather state for each datetime inside the range specified
        forecast = Forecast()
        for data in forecast_data:
            # Filter date range
            forecast_datetime = self._get_forecast_datetime(data)
            in_date_range = start_date <= forecast_datetime.date() <= end_date
            if not in_date_range:
                continue

            # Create weather state and add forecast with its date and timezone to the forecast
            weather_state = self._build_weather_state(data)
            forecast.add(weather_state, forecast_datetime, location_timezone)

        return forecast

    def _get_forecast_datetime(self, forecast) -> datetime:
        try:
            forecast_date_time = datetime.fromtimestamp(forecast["dt"])
        except KeyError:
            raise WeatherStationError("Client data error, missing forecast date")
        return forecast_date_time

    def _get_forecast_data(self, client_data):
        forecasts = client_data.get("list", None)
        if not forecasts:
            raise WeatherStationError("Client data error, missing forecasts list")

        return forecasts

    def _get_timezone(self, client_data):
        try:
            offset_in_seconds = client_data["city"]["timezone"]
            tz = timezone(timedelta(seconds=offset_in_seconds))
        except KeyError:
            raise WeatherStationError("Client data error, missing timezone")
        return tz

    def _build_weather_state(self, client_data):
        weather_state_builder = WeatherStateBuilder()

        main_weather_data = client_data.get("main", {})
        weather_state_builder.with_temperature(main_weather_data.get("temp", None))
        weather_state_builder.with_humidity(main_weather_data.get("humidity", None))
        weather_state_builder.with_feels_like(main_weather_data.get("feels_like", None))
        weather_state_builder.with_pressure(main_weather_data.get("pressure", None))

        wind_data = client_data.get("wind", {})
        weather_state_builder.with_wind_speed(wind_data.get("speed", None))
        weather_state_builder.with_wind_gust(wind_data.get("gust", None))
        weather_state_builder.with_wind_direction(wind_data.get("deg", None))

        clouds_data = client_data.get("clouds", {})
        weather_state_builder.with_clouds(clouds_data.get("all", None))

        rain_data = client_data.get("rain", {})
        weather_state_builder.with_rain_3h(rain_data.get("3h", None))
        weather_state_builder.with_rain_1h(rain_data.get("1h", None))

        snow_data = client_data.get("snow", {})
        weather_state_builder.with_snow_1h(snow_data.get("1h", None))
        weather_state_builder.with_snow_3h(snow_data.get("3h", None))

        # Create weather state and return
        try:
            weather_state = weather_state_builder.build()
        except ValueError as ex:
            raise WeatherStationError(f"Error creating weather state - {ex}")
        return weather_state
