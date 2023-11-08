import pytest

from weather_companion.weather_station import Location


def test_should_create_location_with_valid_data():
    location = Location(51.5074, 0.1278)
    assert location.latitude == 51.5074
    assert location.longitude == 0.1278


def test_should_fail_if_latitude_or_longitude_invalid():
    with pytest.raises(ValueError) as e:
        Location(91, 0)
    assert str(e.value) == "Coordinate must be between -90 and 90"

    with pytest.raises(ValueError) as e:
        Location(-91, 0)
    assert str(e.value) == "Coordinate must be between -90 and 90"

    with pytest.raises(ValueError) as e:
        Location(0, 181)
    assert str(e.value) == "Coordinate must be between -90 and 90"

    with pytest.raises(ValueError) as e:
        Location(0, -181)
    assert str(e.value) == "Coordinate must be between -90 and 90"
