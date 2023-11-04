from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Tuple

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
    ) -> List[Tuple[datetime, str]]:
        """
        Gets the weather forecast for a given latitude and longitude for a given date and time.
        """
        try:
            client_data = self._client.get_forecast(location)
        except ClientError as ex:
            raise WeatherStationError(f"Client error: {ex}")

        forecasts = client_data.get("list", None)
        if not forecasts:
            raise WeatherStationError(
                "Unexpected weather data format: missing forecasts list"
            )

        tz = self._get_timezone(client_data)
        result = []

        # Get weather state for each datetime inside the range specified
        for forecast in forecasts:
            in_date_range = start_date <= date.fromtimestamp(forecast["dt"]) <= end_date
            if not in_date_range:
                continue

            weather_state = self._build_weather_state(forecast)
            date_time = self._get_date_time(tz, forecast)
            result.append((date_time, weather_state))

        return result

    def _get_timezone(self, client_data):
        offset_in_seconds = client_data["city"]["timezone"]
        tz = timezone(timedelta(seconds=offset_in_seconds))
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

    def _get_date_time(self, tz, forecast):
        date_time = datetime.fromtimestamp(forecast["dt"]).replace(tzinfo=tz)
        return date_time
