from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import fastapi
from fastapi import Body, Path, Query
from pydantic import BaseModel

from weather_companion import repository as repo
from weather_companion import system as system
from weather_companion import weather_journal as wj
from weather_companion import weather_station as ws

from . import utils
from .model import Forecast, Journal, JournalEntry, WeatherState
from .user_repository import UserRepository


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

    # Initialize author repository and insert some test users
    user_repository: UserRepository = UserRepository()
    user_repository.add_user("test-user-1", "8fdce8a4-7d6b-11ee-b962-0242ac120001")
    user_repository.add_user("test-user-2", "8fdce8a4-7d6b-11ee-b962-0242ac120002")
    user_repository.add_user("test-user-3", "8fdce8a4-7d6b-11ee-b962-0242ac120003")

    ########################################## Health Check #####################################################

    @app.get("/health", status_code=200)
    async def get_health() -> dict:
        return {"status": "OK"}

    ########################################## Weather Station #################################################

    # Get current weather state
    @app.get(
        "/weather-companion/weather/current",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_current_weather_state(lat: float, long: float, label: str, apikey: str) -> WeatherState:
        _ = utils._validate_user(user_repository=user_repository, apikey=apikey)
        location: ws.Location = utils._deserialize_location(lat, long, label)
        weather_state: WeatherState = utils._get_current_weather_state(weather_companion, location)
        return weather_state

    # Get weather forecast
    @app.get(
        "/weather-companion/weather/forecast",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_weather_forecast(
        lat: float, long: float, label: str, start_date: date, end_date: date, apikey: str
    ) -> Forecast:
        _ = utils._validate_user(user_repository=user_repository, apikey=apikey)
        location: ws.Location = utils._deserialize_location(lat, long, label)
        weather_forecast: ws.Forecast = utils._get_weather_forecast(weather_companion, location, start_date, end_date)
        return utils._serialize_weather_forecast(location, weather_forecast)

    ########################################## Journal #########################################################

    # Post a new journal entry
    @app.post(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def add_journal_entry(journal_entry: JournalEntry, apikey: str = Query(...)) -> int:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        journal_entry: wj.JournalEntry = utils._deserialize_journal_entry(journal_entry)
        id = utils._add_journal_entry(
            weather_companion=weather_companion, journal_entry=journal_entry, author_id=author_id
        )
        return id

    # Get a journal entry
    @app.get(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_entry(entry_id: int, apikey: str = Query(...)) -> JournalEntry:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        journal_entry: wj.JournalEntry = utils._get_journal_entry(entry_id, author_id)
        return utils._serialize_journal_entry(journal_entry)

    # Get all journal entries
    """
    @app.get(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_entries(apikey: str = Query(...)) -> Journal:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        journal = utils._get_entries(weather_companion=weather_companion, author_id=author_id)
        return utils._serialize_journal(journal)
    """

    # Get all filtered journal entries
    @app.get(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_filtered_entries(
        interval: str = Query(None, title="start_date,end_date in YYYY-MM-DD format"),
        region: str = Query(None, title="lat,long,distance"),
        content: str = Query(None, title="content to search for"),
        apikey: str = Query(...),
    ) -> Journal:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        journal = utils._get_entries(weather_companion=weather_companion, author_id=author_id)
        filtered_journal = utils._filter_journal(region=region, interval=interval, content=content, journal=journal)
        return utils._serialize_journal(filtered_journal)

    # Delete a journal entry
    @app.delete(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def delete_entry(entry_id: int, apikey: str = Query(...)) -> bool:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        utils._delete_journal_entry(weather_companion=weather_companion, entry_id=entry_id, author_id=author_id)
        return True

    # Update a journal entry
    @app.patch(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def patch_journal_entry(
        entry_id: int = Path(..., title="journal entry id to update"),
        journal_entry: JournalEntry = Body(..., title="journal entry"),
        apikey: str = Query(...),
    ) -> JournalEntry:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
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
