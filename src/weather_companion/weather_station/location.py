class Location:
    """
    Defines a location.
    """

    def __init__(self, latitude: float, longitude: float, label: str):
        """
        Latitute and Longitude define the location
        """

        # Check that the latitude and longitude have values between -90 and 90
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90")
        if longitude < -90 or longitude > 90:
            raise ValueError("Longitude must be between -90 and 90")

        # Check that the label is not empty or blank string
        label = label.strip()
        if not label:
            raise ValueError("Label must not be empty")

        # Check that label is alpha numeric
        if not label.isalnum():
            raise ValueError("Label must be alphanumeric")

        self.latitude = latitude
        self.longitude = longitude
        self.label = label
