from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

import fastapi

from weather_companion import repository as repo
from weather_companion import system as system
from weather_companion import weather_journal as wj
from weather_companion import weather_station as ws

from .model import (
    Bookmark,
    Bookmarks,
    Forecast,
    ForecastItem,
    Journal,
    JournalEntry,
    JournalItem,
    Location,
    WeatherState,
)
from .user_repository import UserRepository


def _deserialize_location(lat: float, long: float) -> ws.Location:
    try:
        location: ws.Location = ws.Location(latitude=lat, longitude=long)
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
    return location


def _serialize_location(location: ws.Location) -> Location:
    return Location(**location.to_dict())


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


def _serialize_weather_state(weather_state: ws.WeatherState) -> WeatherState:
    return WeatherState(**weather_state.to_dict())


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
        deserialized_journal_entry: wj.JournalEntry = wj.JournalEntry(
            location=ws.Location(**journal_entry.location.model_dump()),
            date=journal_entry.date,
            note=wj.Note(journal_entry.note),
        )
    except Exception as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
    return deserialized_journal_entry


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
    for item in journal:
        entry_id = item[0]
        entry = item[1]
        location = Location(**entry.location().to_dict())
        serialized_item = JournalItem(
            id=entry_id, journal_entry=JournalEntry(note=entry.note().content(), date=entry.date(), location=location)
        )
        serialized_journal.append(serialized_item)
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
        raise fastapi.HTTPException(status_code=401, detail="Invalid User Key Id")
    return user_id


def _get_author_for_key(user_repository: UserRepository, apikey: str) -> wj.AuthorID:
    user_id = _validate_user(user_repository=user_repository, apikey=apikey)
    author_id = wj.AuthorID(user_id)
    return author_id


def _filter_journal(region: str, interval: str, content: str, journal: List[Tuple[int, wj.JournalEntry]]):
    filters = []
    if content is not None:
        content_filter: wj.JournalEntryFilter = wj.NoteContentFilter(content)
        filters.append(content_filter)

    if region is not None:
        # Split regios string "lat;long;distance"
        region_split = region.split(",")
        if len(region_split) != 3:
            raise fastapi.HTTPException(status_code=422, detail="Invalid region format, expected lat;long;distance")
        lat = float(region_split[0])
        long = float(region_split[1])
        distance = float(region_split[2])
        location: ws.Location = ws.Location(latitude=lat, longitude=long)
        region_filter: wj.JournalEntryFilter = wj.LocationProximityFilter(location=location, max_distance=distance)
        filters.append(region_filter)

    if interval is not None:
        # Split interval string "start_date;end_date"
        interval_split = interval.split(",")
        if len(interval_split) != 2:
            raise fastapi.HTTPException(status_code=422, detail="Invalid interval format, expected start_date;end_date")
        start_date = datetime.strptime(interval_split[0], "%Y-%m-%d").date()
        end_date = datetime.strptime(interval_split[1], "%Y-%m-%d").date()
        interval_filter: wj.JournalEntryFilter = wj.DateRangeFilter(start_date=start_date, end_date=end_date)
        filters.append(interval_filter)

    and_filter = wj.AndFilter(filters=filters)
    filtered_journal = [
        (entry_id, journal_entry) for entry_id, journal_entry in journal if and_filter.condition(journal_entry)
    ]
    return filtered_journal


def _serialize_bookmarks(bookmarks: List[Tuple[repo.Bookmark, ws.Location]]) -> Bookmarks:
    serialized_bookmarks = []
    for bookmark, location in bookmarks:
        location = Location(**location.to_dict())
        bookmark_name = bookmark.name()
        bookmark_item = Bookmark(name=bookmark_name, location=location)
        serialized_bookmarks.append(bookmark_item)
    return Bookmarks(bookmarks=serialized_bookmarks)


def _deserialize_bookmark(bookmark: Bookmark) -> repo.Bookmark:
    deserialized_bookmark = repo.Bookmark(name=bookmark.name)
    return deserialized_bookmark


def _add_bookmark(
    weather_companion: system.WeatherCompanion, bookmark: Bookmark, location: ws.Location, author_id: wj.AuthorID
):
    try:
        weather_companion._bookmark_repository.add(bookmark=bookmark, location=location, author_id=author_id)
    except repo.RepositoryError as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))


def _delete_bookmark(weather_companion: system.WeatherCompanion, bookmark: Bookmark, author_id: wj.AuthorID):
    try:
        weather_companion._bookmark_repository.remove(bookmark=bookmark, author_id=author_id)
    except repo.RepositoryError as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))


def _get_current_weather_state_for_bookmark(
    weather_companion: system.WeatherCompanion, bookmark: repo.Bookmark, author_id: wj.AuthorID
) -> ws.WeatherState:
    try:
        location = weather_companion._bookmark_repository.get(bookmark=bookmark, author_id=author_id)
        weather_state = weather_companion.get_current_state(location=location)
    except repo.RepositoryError as e:
        raise fastapi.HTTPException(status_code=400, detail=str(e))
    return weather_state
