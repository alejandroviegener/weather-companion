from datetime import date, datetime, timezone
from typing import List, Tuple

from .weather_state import WeatherState


class Forecast:
    def __init__(self):
        self._forecasts = []

    def add(
        self, weather_state: WeatherState, date_time: datetime, tz: timezone = None
    ) -> None:
        if timezone:
            date_time = date_time.replace(tzinfo=tz)

        # Check datetime is not allready in the list, use sets
        dates_inserted = set([forecast[0] for forecast in self._forecasts])
        if date_time in dates_inserted:
            ValueError("Forecast for this date and time already exists")

        forecast = (date_time, weather_state)
        self._forecasts.append(forecast)

    def get_dates(self) -> List[datetime]:
        # returns a list of datetimes, ordered by date
        dates = [forecast[0] for forecast in self._forecasts]
        dates.sort()
        return dates

    def get_weather_states_for_date(self, date: date) -> List[WeatherState]:
        # Returns a list of weather states for the date specified
        weather_states = []
        for forecast in self._forecasts:
            if forecast[0].date() == date:
                weather_states.append(forecast[1])
        return weather_states

    def __len__(self):
        return len(self._forecasts)
