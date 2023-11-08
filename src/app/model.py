from datetime import date, datetime
from typing import List, Optional, Tuple

from pydantic import BaseModel


class WeatherState(BaseModel):
    temperature: float
    humidity: float
    feels_like: float
    pressure: float
    wind_speed: Optional[float] = None
    wind_gust: Optional[float] = None
    wind_direction: Optional[float] = None
    clouds: Optional[float] = None
    rain_1h: Optional[float] = None
    rain_3h: Optional[float] = None
    snow_1h: Optional[float] = None
    snow_3h: Optional[float] = None


class Location(BaseModel):
    latitude: float
    longitude: float


class ForecastItem(BaseModel):
    date_time: datetime
    weather_state: WeatherState


class Forecast(BaseModel):
    forecast: List[ForecastItem]
    location: Location


class JournalEntry(BaseModel):
    note: str
    date: date
    location: Location


class JournalItem(BaseModel):
    id: int
    journal_entry: JournalEntry


class Journal(BaseModel):
    entries: List[JournalItem]


class Bookmark(BaseModel):
    name: str
    location: Location


class Bookmarks(BaseModel):
    bookmarks: List[Bookmark]
