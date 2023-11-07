from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import fastapi
from fastapi import Body, Path
from pydantic import BaseModel

from weather_companion import repository as repo
from weather_companion import system as system
from weather_companion import weather_journal as wj
from weather_companion import weather_station as ws

from . import utils
from .model import Forecast, Journal, JournalEntry, WeatherState


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

    ########################################## Heath Check #####################################################

    @app.get("/health", status_code=200)
    async def get_health() -> dict:
        return {"status": "OK"}

    ########################################## Weather Station #################################################

    @app.get(
        "/weather-companion/weather/current",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_current_weather_state(lat: float, long: float, label: str) -> WeatherState:
        location: ws.Location = utils._deserialize_location(lat, long, label)
        weather_state: WeatherState = utils._get_current_weather_state(weather_companion, location)
        return weather_state

    @app.get(
        "/weather-companion/weather/forecast",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_weather_forecast(lat: float, long: float, label: str, start_date: date, end_date: date) -> Forecast:
        location: ws.Location = utils._deserialize_location(lat, long, label)
        weather_forecast: ws.Forecast = utils._get_weather_forecast(weather_companion, location, start_date, end_date)
        return utils._serialize_weather_forecast(location, weather_forecast)

    ########################################## Journal #########################################################

    @app.post(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def add_journal_entry(journal_entry: JournalEntry) -> int:
        author_id = wj.AuthorID("test-author-id")
        journal_entry: wj.JournalEntry = utils._deserialize_journal_entry(journal_entry)
        id = utils._add_journal_entry(
            weather_companion=weather_companion, journal_entry=journal_entry, author_id=author_id
        )
        return id

    @app.get(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_entry(entry_id: int) -> JournalEntry:
        author_id = wj.AuthorID("test-author-id")
        journal_entry: wj.JournalEntry = utils._get_journal_entry(entry_id, author_id)
        return utils._serialize_journal_entry(journal_entry)

    @app.get(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_entries() -> Journal:
        author_id = wj.AuthorID("test-author-id")
        journal = utils._get_entries(weather_companion=weather_companion, author_id=author_id)
        return utils._serialize_journal(journal)

    @app.delete(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def delete_entry(entry_id: int) -> None:
        author_id = wj.AuthorID("test-author-id")
        utils._delete_journal_entry(weather_companion=weather_companion, entry_id=entry_id, author_id=author_id)

    @app.patch(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def patch_journal_entry(
        entry_id: int = Path(..., title="journal entry id to update"),
        journal_entry: JournalEntry = Body(..., title="journal entry"),
    ) -> JournalEntry:
        author_id = wj.AuthorID("test-author-id")
        new_journal_entry = utils._deserialize_journal_entry(journal_entry)
        utils._update_journal_entry(
            weather_companion=weather_companion,
            entry_id=entry_id,
            author_id=author_id,
            new_journal_entry=new_journal_entry,
        )
        return journal_entry

    return app


# Read API key from environment variable
import os

# get filepath or use default
model_filepath = os.getenv("MODEL_FILEPATH", "./tmp/delay_model.pkl")
app = create_app(model_filepath)
