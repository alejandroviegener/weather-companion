from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Tuple

import requests

from .base import Location, WeatherStationError


class ClientError(Exception):
    pass


class OpenWeatherMapClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.openweathermap.org/data/2.5"

    def get_current_state(self, location: Location) -> dict:
        """
        Gets the current weather state for a given location.
        """
        try:
            response = requests.get(
                self._base_url
                + f"/weather?lat={location.latitude}&lon={location.longitude}&appid={self._api_key}"
            )
            if response.status_code != 200:
                raise ClientError(
                    f"OpenWeatherMap API returned an error - {response.status_code}-{response.text}"
                )
        except Exception as ex:
            raise ClientError(f"OpenWeatherMap API error - {ex}")

        return response.json()

    def get_forecast(self, location: Location) -> dict:
        """
        Gets the weather forecast for a location, given a start and end date.
        """
        try:
            response = requests.get(
                self._base_url
                + f"/forecast?lat={location.latitude}&lon={location.longitude}&appid={self._api_key}"
            )

            if response.status_code != 200:
                raise ClientError(
                    f"OpenWeatherMap API returned an error - {response.status_code}-{response.text}"
                )
        except Exception as ex:
            raise ClientError(f"OpenWeatherMap API error - {ex}")

        return response.json()


class OWMWeatherStation:
    """
    Defines a weather forecast provider that uses OpenWeatherMap.
    """

    def __init__(self, client: OpenWeatherMapClient):
        """
        Creates a new instance of the OpenWeatherMap class.
        """
        self._client = client

    def get_current_state(self, location):
        """
        Gets the current weather state for a given location.
        """
        try:
            weather_data = self._client.get_current_state(location)
        except ClientError as ex:
            raise WeatherStationError(f"Client error: {ex}")

        # Get mandatory and optional data
        mandatory_weather_data = self._get_mandatory_weather_data(weather_data)
        optional_weather_data = self._get_optional_weather_data(weather_data)

        weather_data = {}
        weather_data.update(mandatory_weather_data)
        weather_data.update(optional_weather_data)
        return {"weather_data": weather_data}

    def get_forecast(
        self, location: Location, start_date: date, end_date: date
    ) -> List[Tuple[datetime, str]]:
        """
        Gets the weather forecast for a given latitude and longitude for a given date and time.
        """
        try:
            forecast_data = self._client.get_forecast(location)
        except ClientError as ex:
            raise WeatherStationError(f"Client error: {ex}")

        if not forecast_data.get("list", None):
            raise WeatherStationError(
                "Unexpected weather data format: missing forecasts list"
            )

        # Get mandatory and optional data for each forecast instance and add it to the result
        forecast_list = []
        for forecast in forecast_data["list"]:
            in_date_range = start_date <= date.fromtimestamp(forecast["dt"]) <= end_date
            if not in_date_range:
                continue

            weather_data = {}
            mandatory_weather_data = self._get_mandatory_weather_data(forecast)
            optional_weather_data = self._get_optional_weather_data(forecast)

            weather_data.update(mandatory_weather_data)
            weather_data.update(optional_weather_data)

            offset_in_seconds = forecast_data["city"]["timezone"]
            tz = timezone(timedelta(seconds=offset_in_seconds))
            date_time = datetime.fromtimestamp(forecast["dt"]).replace(tzinfo=tz)

            forecast_list.append(
                {
                    "weather": weather_data,
                    "date_time": date_time.isoformat(),
                    "city_name": forecast_data["city"]["name"],
                    "country_code": forecast_data["city"]["country"]
                    if forecast_data["city"]["country"]
                    else "-",
                }
            )

        return forecast_list

    def _get_mandatory_weather_data(self, source: Dict) -> Dict:
        weather_data = source.get("main", None)
        if not weather_data:
            raise WeatherStationError(
                "Unexpected weather data fromat: missing main field"
            )

        mandatory_fields = ["temp", "humidity", "feels_like", "pressure"]
        temperature, humidity, feels_like, pressure = self._get_mandatory_fields(
            source=weather_data, fields=mandatory_fields
        )
        return {
            "temperature": temperature,
            "humidity": humidity,
            "feels_like": feels_like,
            "pressure": pressure,
        }

    def _get_mandatory_fields(self, source: Dict, fields: List[str]) -> List:
        values = []
        for field_name in fields:
            value = source.get(field_name, None)
            if not value:
                raise WeatherStationError(f"no {field_name} field found")
            values.append(value)
        return values

    def _get_optional_weather_data(self, source: Dict) -> Dict:
        optional_data = {}
        wind_data = self._get_optional_wind_data(source=source.get("wind", {}))
        clouds_data = self._get_optional_clouds_data(source=source.get("clouds", {}))
        rain_data = self._get_optional_rain_data(source=source.get("rain", {}))
        snow_data = self._get_optional_snow_data(source=source.get("snow", {}))

        optional_data = {}
        optional_data.update(wind_data)
        optional_data.update(clouds_data)
        optional_data.update(rain_data)
        optional_data.update(snow_data)
        return optional_data

    def _get_optional_wind_data(self, source: Dict) -> Dict:
        wind_data = {}

        wind_speed = source.get("speed", None)
        if wind_speed:
            wind_data.update({"wind_speed": wind_speed})
        wind_gust = source.get("gust", None)
        if wind_gust:
            wind_data.update({"wind_gust": wind_gust})
        wind_direction = source.get("deg", None)
        if wind_direction:
            wind_data.update({"wind_direction": wind_direction})
        return wind_data

    def _get_optional_clouds_data(self, source: Dict) -> Dict:
        clouds_data = {}

        clouds = source.get("all", None)
        if clouds:
            clouds_data.update({"clouds": clouds})
        return clouds_data

    def _get_optional_rain_data(self, source: Dict) -> Dict:
        rain_data = {}

        rain = source.get("1h", None)
        if rain:
            rain_data.update({"rain_1h": rain})
        rain = source.get("3h", None)
        if rain:
            rain_data.update({"rain_3h": rain})
        return rain_data

    def _get_optional_snow_data(self, source: Dict) -> Dict:
        snow_data = {}

        snow = source.get("1h", None)
        if snow:
            snow_data.update({"snow_1h": snow})
        snow = source.get("3h", None)
        if snow:
            snow_data.update({"snow_3h": snow})
        return snow_data
