"""
Defines weather state class and Builder
"""

from typing import Dict, NamedTuple


class WeatherState(NamedTuple):
    # Mandatory
    temperature: float
    humidity: float
    feels_like: float
    pressure: float
    # Optional
    wind_speed: float = None
    wind_gust: float = None
    wind_direction: float = None
    clouds: float = None
    rain_1h: float = None
    rain_3h: float = None
    snow_1h: float = None
    snow_3h: float = None

    def to_dict(self) -> Dict:
        result = {}
        result.update({"temperature": self.temperature})
        result.update({"humidity": self.humidity})
        result.update({"feels_like": self.feels_like})
        result.update({"pressure": self.pressure})
        if self.wind_speed:
            result.update({"wind_speed": self.wind_speed})
        if self.wind_gust:
            result.update({"wind_gust": self.wind_gust})
        if self.wind_direction:
            result.update({"wind_direction": self.wind_direction})
        if self.clouds:
            result.update({"clouds": self.clouds})
        if self.rain_1h:
            result.update({"rain_1h": self.rain_1h})
        if self.rain_3h:
            result.update({"rain_3h": self.rain_3h})
        if self.snow_1h:
            result.update({"snow_1h": self.snow_1h})
        if self.snow_3h:
            result.update({"snow_3h": self.snow_3h})

        return result


class WeatherStateBuilder:
    """
    Creates WeatherState objects, validates mandatory data and consistency
    """

    def __init__(self) -> None:
        self._temperature = None
        self._humidity = None
        self._feels_like = None
        self._pressure = None
        self._wind_speed = None
        self._wind_gust = None
        self._wind_direction = None
        self._clouds = None
        self._rain_1h = None
        self._rain_3h = None
        self._snow_1h = None
        self._snow_3h = None

    def with_temperature(self, temperature: float) -> None:
        self._temperature = temperature
        return self

    def with_humidity(self, humidity: float) -> None:
        self._humidity = humidity
        return self

    def with_feels_like(self, feels_like: float) -> None:
        self._feels_like = feels_like
        return self

    def with_pressure(self, pressure: float) -> None:
        self._pressure = pressure
        return self

    def with_wind_speed(self, wind_speed: float) -> None:
        self._wind_speed = wind_speed
        return self

    def with_wind_gust(self, wind_gust: float) -> None:
        self._wind_gust = wind_gust
        return self

    def with_wind_direction(self, wind_direction: float) -> None:
        self._wind_direction = wind_direction
        return self

    def with_clouds(self, clouds: float) -> None:
        self._clouds = clouds
        return self

    def with_rain_1h(self, rain_1h: float) -> None:
        self._rain_1h = rain_1h
        return self

    def with_rain_3h(self, rain_3h: float) -> None:
        self._rain_3h = rain_3h
        return self

    def with_snow_1h(self, snow_1h: float) -> None:
        self._snow_1h = snow_1h
        return self

    def with_snow_3h(self, snow_3h: float) -> None:
        self._snow_3h = snow_3h
        return self

    def build(self) -> WeatherState:
        self._validate_mandatory_data_is_present()
        self._validate_data_consistency()
        return WeatherState(
            temperature=self._temperature,
            humidity=self._humidity,
            feels_like=self._feels_like,
            pressure=self._pressure,
            wind_speed=self._wind_speed,
            wind_gust=self._wind_gust,
            wind_direction=self._wind_direction,
            clouds=self._clouds,
            rain_1h=self._rain_1h,
            rain_3h=self._rain_3h,
            snow_1h=self._snow_1h,
            snow_3h=self._snow_3h,
        )

    def _validate_mandatory_data_is_present(self) -> None:
        self._check_value_is_not_none(self._temperature, "temperature")
        self._check_value_is_not_none(self._humidity, "humidity")
        self._check_value_is_not_none(self._feels_like, "feels like")
        self._check_value_is_not_none(self._pressure, "pressure")

    def _validate_data_consistency(self) -> None:
        self._check_is_positive_number_if_not_none(self._wind_gust, "wind gust")
        self._check_is_valid_angle_if_not_none(self._wind_direction, "wind direction")
        self._check_is_valid_percentage_if_not_none(self._clouds, "clouds")
        self._check_is_positive_number_if_not_none(self._rain_1h, "rain 1h")
        self._check_is_positive_number_if_not_none(self._rain_3h, "rain 3h")
        self._check_is_positive_number_if_not_none(self._snow_1h, "snow 1h")
        self._check_is_positive_number_if_not_none(self._snow_3h, "snow 3h")
        self._check_is_valid_percentage_if_not_none(self._humidity, "humidity")
        self._check_is_positive_number_if_not_none(self._pressure, "pressure")

    @staticmethod
    def _check_value_is_not_none(value, variable_name: str):
        if value is None:
            raise ValueError(f"{variable_name} is mandatory")

    @staticmethod
    def _check_is_valid_percentage_if_not_none(value, variable_name: str):
        if value is not None and (value < 0 or value > 100):
            raise ValueError(f"{variable_name} should be a value between 0 and 100")

    @staticmethod
    def _check_is_valid_angle_if_not_none(value, variable_name: str):
        if value is not None and (value < 0 or value > 360):
            raise ValueError(f"{variable_name} should be a value between 0 and 360")

    @staticmethod
    def _check_is_positive_number_if_not_none(value, variable_name: str):
        if value is not None and value < 0:
            raise ValueError(f"{variable_name} should be a positive number")
