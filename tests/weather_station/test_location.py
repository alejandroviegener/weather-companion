import pytest

from weather_companion.weather_station import Location


def test_should_create_location_with_valid_data():
    location = Location(51.5074, 0.1278, "London")
    assert location.latitude == 51.5074
    assert location.longitude == 0.1278
    assert location.label == "London"


def test_should_fail_if_latitude_or_longitude_invalid():
    with pytest.raises(ValueError):
        Location(91, 0, "London")
    with pytest.raises(ValueError):
        Location(-91, 0, "London")
    with pytest.raises(ValueError):
        Location(0, 181, "London")
    with pytest.raises(ValueError):
        Location(0, -181, "London")


def test_should_fail_if_invalid_name():
    with pytest.raises(ValueError):
        Location(51.5074, 0.1278, "")
    with pytest.raises(ValueError):
        Location(51.5074, 0.1278, " ")
    with pytest.raises(ValueError):
        Location(51.5074, 0.1278, "London!")
