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
from .model import (
    Bookmark,
    Bookmarks,
    Forecast,
    Journal,
    JournalEntry,
    Location,
    WeatherState,
)
from .user_repository import UserRepository

APIKEY_DESCRIPTION = "user api key"


def create_app(weather_client_api_key: str) -> fastapi.FastAPI:
    #  # Initialize System
    app = fastapi.FastAPI(
        title="Weather Companion API",
        version="0.1.0",
        description="Api that serves as a weather related info companion for your trips and day to day life",
    )
    weather_companion: system.WeatherCompanion = _initialize_weather_companion_system(weather_client_api_key)
    user_repository: UserRepository = _initialize_user_repository()

    ########################################## Health Check #####################################################

    @app.get("/health", status_code=200, tags=["Health"], summary="Health check")
    async def get_health() -> dict:
        return {"status": "OK"}

    ########################################## Weather Station #################################################

    # Get current weather state
    @app.get(
        "/weather-companion/weather/current",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Weather"],
        summary="Get current weather state for a specified location",
    )
    async def get_current_weather_state(
        lat: float = Query(..., description="coordinate between [-90, 90]"),
        long: float = Query(..., description="coordinate between [-90, 90]"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
    ) -> WeatherState:
        _ = utils._validate_user(user_repository=user_repository, apikey=apikey)
        location: ws.Location = utils._deserialize_location(lat, long)
        weather_state: WeatherState = utils._get_current_weather_state(weather_companion, location)
        return weather_state

    # Get weather forecast
    @app.get(
        "/weather-companion/weather/forecast",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Weather"],
        summary="Get weather forecast for a specified location and date range",
    )
    async def get_weather_forecast(
        lat: float = Query(..., description="coordinate between [-90, 90]"),
        long: float = Query(..., description="coordinate between [-90, 90]"),
        start_date: date = Query(..., description="date in YYYY-MM-DD format"),
        end_date: date = Query(..., description="date in YYYY-MM-DD format"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
    ) -> Forecast:
        _ = utils._validate_user(user_repository=user_repository, apikey=apikey)
        location: ws.Location = utils._deserialize_location(lat, long)
        weather_forecast: ws.Forecast = utils._get_weather_forecast(weather_companion, location, start_date, end_date)
        return utils._serialize_weather_forecast(location, weather_forecast)

    ########################################## Journal #########################################################

    # Post a new journal entry
    @app.post(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Journal"],
        summary="Add a new entry note to the journal for a specified location",
    )
    async def add_journal_entry(
        journal_entry: JournalEntry = Body(..., description="entry with note, date and location"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
    ) -> int:
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
        tags=["Journal"],
        summary="Get a specific entry note from the journal",
    )
    async def get_entry(
        entry_id: int = Path(..., description="entry id to get"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
    ) -> JournalEntry:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        journal_entry: wj.JournalEntry = utils._get_journal_entry(
            weather_companion=weather_companion, entry_id=entry_id, author_id=author_id
        )
        return utils._serialize_journal_entry(journal_entry)

    # Get all filtered journal entries
    @app.get(
        "/weather-companion/journal/entries",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Journal"],
        summary="Get all entry notes from the journal according to the specified filters",
    )
    async def get_filtered_entries(
        interval: str = Query(None, description="start_date,end_date in YYYY-MM-DD format"),
        region: str = Query(None, description="lat,long,distance"),
        content: str = Query(None, description="content to search for"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
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
        tags=["Journal"],
        summary="Delete a specific entry note from the journal",
    )
    async def delete_entry(
        entry_id: int = Path(..., description="entry id to delete"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
    ) -> str:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        utils._delete_journal_entry(weather_companion=weather_companion, entry_id=entry_id, author_id=author_id)
        return "success"

    # Update a journal entry
    @app.patch(
        "/weather-companion/journal/entries/{entry_id}",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Journal"],
        summary="Update a specific entry note from the journal",
    )
    async def patch_journal_entry(
        entry_id: int = Path(..., description="journal entry id to update"),
        journal_entry: JournalEntry = Body(..., description="journal entry"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
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

    ########################################## Bookmarks #######################################################

    @app.get(
        "/weather-companion/bookmarks",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Bookmarks"],
        summary="Get all the location bookmarks",
    )
    async def get_all_bookmarks(apikey: str = Query(..., description=APIKEY_DESCRIPTION)):
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        bookmarks: List[Tuple[wj.Bookmark, ws.Location]] = weather_companion._bookmark_repository.get_all_bookmarks(
            author_id
        )
        return utils._serialize_bookmarks(bookmarks=bookmarks)

    @app.post(
        "/weather-companion/bookmarks",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Bookmarks"],
        summary="Add a new location bookmark",
    )
    async def add_bookmark(bookmark: Bookmark, apikey: str = Query(..., description=APIKEY_DESCRIPTION)) -> Bookmark:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        deserialized_location: ws.Location = utils._deserialize_location(
            lat=bookmark.location.latitude, long=bookmark.location.longitude
        )
        deserialized_bookmark: wj.Bookmark = utils._deserialize_bookmark(bookmark=bookmark)
        utils._add_bookmark(
            weather_companion=weather_companion,
            bookmark=deserialized_bookmark,
            location=deserialized_location,
            author_id=author_id,
        )
        return bookmark

    @app.delete(
        "/weather-companion/bookmarks/{name}",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Bookmarks"],
        summary="Delete a location bookmark",
    )
    async def delete_bookmark(
        name: str = Path(..., description="bockmark name to delete"),
        apikey: str = Query(..., description=APIKEY_DESCRIPTION),
    ) -> str:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        bookmark: repo.Bookmark = repo.Bookmark(name=name)
        utils._delete_bookmark(
            weather_companion=weather_companion,
            bookmark=bookmark,
            author_id=author_id,
        )
        return "success"

    @app.get(
        "/weather-companion/bookmarks/{name}/weather/current",
        status_code=200,
        response_model_exclude_none=True,
        tags=["Bookmarks"],
        summary="Get the current weather state for a specified location bookmark",
    )
    async def get_current_weather_for_bookmark(
        name: str = Path(..., description="bockmark name"), apikey: str = Query(..., description=APIKEY_DESCRIPTION)
    ) -> WeatherState:
        author_id: wj.AuthorID = utils._get_author_for_key(user_repository=user_repository, apikey=apikey)
        bookmark: wj.Bookmark = wj.Bookmark(name=name)
        weather_state: ws.WeatherState = utils._get_current_weather_state_for_bookmark(
            weather_companion=weather_companion,
            bookmark=bookmark,
            author_id=author_id,
        )
        return utils._serialize_weather_state(weather_state=weather_state)

    return app


def _initialize_weather_companion_system(weather_client_api_key: str):
    weather_station_client = ws.OWMClient(api_key=weather_client_api_key)
    weather_station: ws.WeatherStation = ws.OWMWeatherStation(client=weather_station_client)
    weather_companion: system.WeatherCompanion = system.WeatherCompanion(
        weather_station=weather_station,
        journal_repository=repo.InMemoryJournalRepository(),
        bookmark_repository=repo.InMemoryLocationBookmarkRepository(),
    )

    return weather_companion


def _initialize_user_repository():
    user_repository: UserRepository = UserRepository()
    user_repository.add_user("test-user-1", "8fdce8a4-7d6b-11ee-b962-0242ac120001")
    user_repository.add_user("test-user-2", "8fdce8a4-7d6b-11ee-b962-0242ac120002")
    user_repository.add_user("test-user-3", "8fdce8a4-7d6b-11ee-b962-0242ac120003")
    return user_repository


# Read API key from environment variable
import os

# get filepath or use default
weather_client_api_key = os.getenv("WEATHER_CLIENT_API_KEY", None)
if weather_client_api_key is None:
    raise ValueError("WEATHER_CLIENT_API_KEY environment variable not set")

print(weather_client_api_key)
app = create_app(weather_client_api_key)
