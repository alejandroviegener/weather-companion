from geopy.distance import geodesic


class Location:
    """
    Defines a location.
    """

    def __init__(self, latitude: float, longitude: float):
        """
        Latitute and Longitude define the location
        """

        # Check that the latitude and longitude have values between -90 and 90
        self._check_is_valid_coordinate(latitude)
        self._check_is_valid_coordinate(longitude)

        self.latitude = latitude
        self.longitude = longitude

    def distance_to(self, other) -> float:
        """
        Returns the distance to another location in km
        """
        return geodesic((self.latitude, self.longitude), (other.latitude, other.longitude)).km

    def to_dict(self):
        return {"latitude": self.latitude, "longitude": self.longitude}

    def _check_is_valid_coordinate(self, coordinate):
        if coordinate < -90 or coordinate > 90:
            raise ValueError("Coordinate must be between -90 and 90")

    def __eq__(self, other):
        return self.latitude == other.latitude and self.longitude == other.longitude
