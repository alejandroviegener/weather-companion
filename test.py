import os
from datetime import datetime, timedelta

from src.weather_companion.weather_station import Location, OWMClient, OWMWeatherStation

if __name__ == "__main__":
    # read api key from env variable
    api_key = os.environ.get("OPEN_WEATHER_MAP_API_KEY")

    client = OWMClient(api_key)
    weather_station = OWMWeatherStation(client)

    # san nicolas, lat-34.6037&lon=-58.3816
    location = Location(longitude=-58.3816, latitude=-34.6037, label="SanNicolas")

    current_state = weather_station.get_current_state(location)
    print("current state:")
    print(current_state)

    forecast = weather_station.get_forecast(
        location,
        start_date=datetime.now().date(),
        end_date=datetime.now().date() + timedelta(days=2),
    )

    print("forecast dates:")
    print([str(d) for d in forecast.get_dates()])

    print("full forecast")
    print([(str(d), s) for (d, s) in list(forecast)])
