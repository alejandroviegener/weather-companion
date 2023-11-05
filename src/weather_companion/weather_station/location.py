class Location:
    """
    Defines a location.
    """

    def __init__(self, latitude: float, longitude: float, label: str):
        """
        Latitute and Longitude define the location
        """

        # Check that the latitude and longitude have values between -90 and 90
        self._check_is_valid_coordinate(latitude)
        self._check_is_valid_coordinate(longitude)

        # Check that the label is valid
        label = self._check_is_not_blank(label)
        self._check_is_alpha(label)

        self.latitude = latitude
        self.longitude = longitude
        self.label = label

    def _check_is_alpha(self, label):
        if not label.isalnum():
            raise ValueError("Label must be alphanumeric")

    def _check_is_not_blank(self, label):
        label = label.strip()
        if not label:
            raise ValueError("Label must not be empty")
        return label

    def _check_is_valid_coordinate(self, coordinate):
        if coordinate < -90 or coordinate > 90:
            raise ValueError("Coordinate must be between -90 and 90")

    def __eq__(self, other):
        return (
            self.latitude == other.latitude
            and self.longitude == other.longitude
            and self.label == other.label
        )
