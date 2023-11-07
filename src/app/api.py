from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import fastapi
from fastapi import Body, Path
from pydantic import BaseModel

from weather_companion import repository as repo
from weather_companion import system as system
from weather_companion import weather_journal as wj
from weather_companion import weather_station as ws


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


def create_app(model_filepath: str) -> fastapi.FastAPI:
    # Create app
    app = fastapi.FastAPI()

    # Initialize weather station
    weather_station_client = ws.OWMClient(api_key="cc803778f0556511257a09dc0789f825")
    weather_station: ws.WeatherStation = ws.OWMWeatherStation(client=weather_station_client)

    # Initialize weather companion
    weather_companion: system.WeatherCompanion = system.WeatherCompanion(
        weather_station=weather_station,
        journal_repository=repo.InMemoryJournalRepository(),
    )

    # Define API endpoints
    @app.get("/health", status_code=200)
    async def get_health() -> dict:
        return {"status": "OK"}

    @app.get(
        "/weather-companion/weather/current",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_current_weather_state(lat: float, long: float, label: str) -> WeatherState:
        location: ws.Location = _get_location(lat, long, label)
        weather_state = _get_current_weather_state(weather_companion, location)

        return WeatherState(**weather_state.to_dict())

    @app.get(
        "/weather-companion/weather/forecast",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_weather_forecast(lat: float, long: float, label: str, start_date: date, end_date: date) -> Forecast:
        location: ws.Location = _get_location(lat, long, label)
        weather_forecast: ws.Forecast = _get_weather_forecast(weather_companion, location, start_date, end_date)

        serialized_forecast = []
        for wf in weather_forecast:
            wfi = ForecastItem(date_time=wf[0], weather_state=WeatherState(**wf[1].to_dict()))
            serialized_forecast.append(wfi)
        return Forecast(forecast=serialized_forecast, location=Location(**location.to_dict()))

    @app.post(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def add_journal_entry(journal_entry: JournalEntry) -> int:
        try:
            author_id = wj.AuthorID("test-author-id")
            journal_entry: wj.JournalEntry = wj.JournalEntry(
                location=ws.Location(**journal_entry.location.model_dump(), label="testlocation"),
                date=journal_entry.date,
                note=journal_entry.note,
            )
        except Exception as e:
            raise fastapi.HTTPException(status_code=400, detail=str(e))
        try:
            id = weather_companion.add_journal_entry(author=author_id, journal_entry=journal_entry)
        except Exception as e:
            raise fastapi.HTTPException(status_code=500, detail=str(e))
        return id

    @app.get(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_entry(entry_id: int) -> JournalEntry:
        try:
            author_id = wj.AuthorID("test-author-id")
            journal_entry: wj.JournalEntry = weather_companion.get_journal_entry(
                author=author_id, journal_entry_id=entry_id
            )
        except Exception as e:
            raise fastapi.HTTPException(status_code=500, detail=str(e))
        return JournalEntry(
            note=journal_entry.note(),
            date=journal_entry.date(),
            location=Location(**journal_entry.location().to_dict()),
        )

    @app.get(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_entries() -> Journal:
        try:
            author_id = wj.AuthorID("test-author-id")
            journal: List[Tuple[int, JournalEntry]] = weather_companion.get_all_journal_entries(author=author_id)
        except Exception as e:
            raise fastapi.HTTPException(status_code=500, detail=str(e))

        serialized_journal = []
        for j in journal:
            ji = JournalItem(
                id=j[0],
                journal_entry=JournalEntry(
                    note=j[1].note(), date=j[1].date(), location=Location(**j[1].location().to_dict())
                ),
            )
            serialized_journal.append(ji)
        return Journal(entries=serialized_journal)

    @app.delete(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def delete_entry(entry_id: int) -> None:
        try:
            author_id = wj.AuthorID("test-author-id")
            weather_companion.remove_journal_entry(author=author_id, journal_entry_id=entry_id)
        except Exception as e:
            raise fastapi.HTTPException(status_code=500, detail=str(e))

    @app.patch(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def patch_journal_entry(
        entry_id: int = Path(..., title="journal entry id to update"),
        journal_entry: JournalEntry = Body(..., title="journal entry"),
    ) -> JournalEntry:
        try:
            author_id = wj.AuthorID("test-author-id")
            new_journal_entry: wj.JournalEntry = wj.JournalEntry(
                location=ws.Location(**journal_entry.location.model_dump(), label="testlocation"),
                date=journal_entry.date,
                note=journal_entry.note,
            )
        except Exception as e:
            raise fastapi.HTTPException(status_code=400, detail=str(e))
        try:
            weather_companion.update_journal_entry(
                journal_entry_id=entry_id, author=author_id, new_journal_entry=new_journal_entry
            )
        except Exception as e:
            raise fastapi.HTTPException(status_code=500, detail=str(e))
        return journal_entry

    return app


# Read API key from environment variable
import os

# get filepath or use default
model_filepath = os.getenv("MODEL_FILEPATH", "./tmp/delay_model.pkl")
app = create_app(model_filepath)


#######################################################################################################################
################################################## Utils ##############################################################
#######################################################################################################################


def _get_location(lat, long, label) -> ws.Location:
    try:
        location: ws.Location = ws.Location(latitude=lat, longitude=long, label=label)
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
    return location


def _get_current_weather_state(weather_companion: system.WeatherCompanion, location: ws.Location) -> ws.WeatherState:
    try:
        weather_state: ws.WeatherState = weather_companion.get_current_state(location)
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    return weather_state


def _get_weather_forecast(
    weather_companion: system.WeatherCompanion,
    location: ws.Location,
    start_date: date,
    end_date: date,
) -> ws.Forecast:
    try:
        weather_forecast: ws.Forecast = weather_companion.get_forecast(
            location=location, start_date=start_date, end_date=end_date
        )
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))

    return weather_forecast
