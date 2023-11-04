import requests

from .location import Location


class ClientError(Exception):
    pass


class OWMClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.openweathermap.org/data/2.5"

        # @TODO: add retry and timeout policy

    def get_current_state(self, location: Location) -> dict:
        """
        Gets the current weather state for a given location.
        """
        endpoint = (
            self._base_url
            + f"/weather?lat={location.latitude}&lon={location.longitude}&appid={self._api_key}"
        )
        response = self._request(endpoint)
        return response.json()

    def get_forecast(self, location: Location) -> dict:
        """
        Gets the weather forecast for a location, given a start and end date.
        """
        endpoint = (
            self._base_url
            + f"/forecast?lat={location.latitude}&lon={location.longitude}&appid={self._api_key}"
        )
        response = self._request(endpoint)
        return response.json()

    def _request(self, endpoint):
        try:
            response = requests.get(endpoint)
            if response.status_code != 200:
                raise ClientError(
                    f"OpenWeatherMap API returned an error - {response.status_code} - {response.text}"
                )
        except Exception as ex:
            raise ClientError(f"OpenWeatherMap API error - {ex}")
        return response
