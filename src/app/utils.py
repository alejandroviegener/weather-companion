from datetime import date
from typing import Dict, List, Optional, Tuple

import fastapi

from weather_companion import repository as repo
from weather_companion import system as system
from weather_companion import weather_journal as wj
from weather_companion import weather_station as ws

from .model import (
    Forecast,
    ForecastItem,
    Journal,
    JournalEntry,
    JournalItem,
    Location,
    WeatherState,
)
from .user_repository import UserRepository


def _deserialize_location(lat, long, label) -> ws.Location:
    try:
        location: ws.Location = ws.Location(latitude=lat, longitude=long, label=label)
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
    return location


def _get_current_weather_state(weather_companion: system.WeatherCompanion, location: ws.Location) -> WeatherState:
    try:
        weather_state: ws.WeatherState = weather_companion.get_current_state(location)
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    return WeatherState(**weather_state.to_dict())


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


def _serialize_weather_forecast(location: ws.Location, weather_forecast: ws.Forecast) -> Forecast:
    serialized_forecast = []
    for wf in weather_forecast:
        date_time = wf[0]
        weather_state = wf[1]
        forecast_item = ForecastItem(date_time=date_time, weather_state=WeatherState(**weather_state.to_dict()))
        serialized_forecast.append(forecast_item)
    return Forecast(forecast=serialized_forecast, location=Location(**location.to_dict()))


def _add_journal_entry(
    weather_companion: system.WeatherCompanion, journal_entry: wj.JournalEntry, author_id: wj.AuthorID
) -> int:
    try:
        id = weather_companion.add_journal_entry(author=author_id, journal_entry=journal_entry)
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    return id


def _deserialize_journal_entry(journal_entry: JournalEntry) -> wj.JournalEntry:
    try:
        journal_entry: wj.JournalEntry = wj.JournalEntry(
            location=ws.Location(**journal_entry.location.model_dump(), label="testlocation"),
            date=journal_entry.date,
            note=journal_entry.note,
        )
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
    return journal_entry


def _get_journal_entry(
    weather_companion: system.WeatherCompanion, entry_id: int, author_id: wj.AuthorID
) -> wj.JournalEntry:
    journal_entry: wj.JournalEntry = None
    try:
        journal_entry: wj.JournalEntry = weather_companion.get_journal_entry(
            author=author_id, journal_entry_id=entry_id
        )
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    return journal_entry


def _serialize_journal_entry(journal_entry: wj.JournalEntry) -> JournalEntry:
    serialized_journal_entry = JournalEntry(
        note=journal_entry.note(),
        date=journal_entry.date(),
        location=Location(**journal_entry.location().to_dict()),
    )
    return serialized_journal_entry


def _serialize_journal(journal: List[Tuple[int, wj.JournalEntry]]) -> Journal:
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


def _get_entries(
    weather_companion: system.WeatherCompanion, author_id: wj.AuthorID
) -> List[Tuple[int, wj.JournalEntry]]:
    try:
        journal: List[Tuple[int, JournalEntry]] = weather_companion.get_all_journal_entries(author=author_id)
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))
    return journal


def _delete_journal_entry(weather_companion: system.WeatherCompanion, entry_id: int, author_id: wj.AuthorID) -> None:
    try:
        weather_companion.remove_journal_entry(author=author_id, journal_entry_id=entry_id)
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))


def _update_journal_entry(
    weather_companion: system.WeatherCompanion,
    entry_id: int,
    author_id: wj.AuthorID,
    new_journal_entry: wj.JournalEntry,
):
    try:
        weather_companion.update_journal_entry(
            journal_entry_id=entry_id, author=author_id, new_journal_entry=new_journal_entry
        )
    except Exception as e:
        raise fastapi.HTTPException(status_code=500, detail=str(e))


def _validate_user(user_repository: UserRepository, apikey: str) -> str:
    try:
        user_id = user_repository.get_user(apikey)
    except KeyError:
        raise fastapi.HTTPException(status_code=401, detail="Invalid API key")
    return user_id


def _get_author_for_key(user_repository: UserRepository, apikey: str) -> wj.AuthorID:
    user_id = _validate_user(user_repository=user_repository, apikey=apikey)
    author_id = wj.AuthorID(user_id)
    return author_id
