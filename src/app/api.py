from datetime import date, datetime
from typing import List, Optional

import fastapi
from pydantic import BaseModel


class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int


class PredictionRequest(BaseModel):
    flights: List[Flight]


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


class GetCurrentWeatherResponse(BaseModel):
    current_state: WeatherState
    location: Location


class WeatherForecastItem(BaseModel):
    date_time: datetime
    weather_state: WeatherState


class GetWeatherForecastResponse(BaseModel):
    forecast: List[WeatherForecastItem]
    location: Location


from weather_companion import repository as repo
from weather_companion import system as system
from weather_companion import weather_station as ws


def create_app(model_filepath: str) -> fastapi.FastAPI:
    # Create app
    app = fastapi.FastAPI()

    # Initialize weather station
    weather_station_client = ws.OWMClient(api_key="cc803778f0556511257a09dc0789f825")
    weather_station: ws.WeatherStation = ws.OWMWeatherStation(
        client=weather_station_client
    )

    # Initialize weather companion
    weather_companion: system.WeatherCompanion = system.WeatherCompanion(
        weather_station=weather_station,
        journal_repository=repo.InMemoryJournalRepository,
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
    async def get_current_weather_state(
        lat: float, long: float, label: str
    ) -> GetCurrentWeatherResponse:
        location: ws.Location = _get_location(lat, long, label)
        weather_state = _get_current_weather_state(weather_companion, location)

        return GetCurrentWeatherResponse(
            current_state=WeatherState(**weather_state.to_dict()),
            location=Location(**location.to_dict()),
        )

    @app.get(
        "/weather-companion/weather/forecast",
        status_code=200,
        response_model_exclude_none=True,
    )
    async def get_weather_forecast(
        lat: float, long: float, label: str, start_date: date, end_date: date
    ) -> GetWeatherForecastResponse:
        location: ws.Location = _get_location(lat, long, label)
        weather_forecast: ws.Forecast = _get_weather_forecast(
            weather_companion, location, start_date, end_date
        )

        serialized_forecast = []
        for wf in weather_forecast:
            wfi = WeatherForecastItem(
                date_time=wf[0], weather_state=WeatherState(**wf[1].to_dict())
            )
            serialized_forecast.append(wfi)
        return GetWeatherForecastResponse(
            forecast=serialized_forecast, location=Location(**location.to_dict())
        )

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


def _get_current_weather_state(
    weather_companion: system.WeatherCompanion, location: ws.Location
) -> ws.WeatherState:
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
