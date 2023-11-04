import pytest

from weather_companion.weather_station import Location


def test_should_create_location_with_valid_data():
    location = Location(51.5074, 0.1278, "London")
    assert location.latitude == 51.5074
    assert location.longitude == 0.1278
    assert location.label == "London"


def test_should_fail_if_latitude_or_longitude_invalid():
    with pytest.raises(ValueError) as e:
        Location(91, 0, "London")
    assert str(e.value) == "Coordinate must be between -90 and 90"

    with pytest.raises(ValueError) as e:
        Location(-91, 0, "London")
    assert str(e.value) == "Coordinate must be between -90 and 90"

    with pytest.raises(ValueError) as e:
        Location(0, 181, "London")
    assert str(e.value) == "Coordinate must be between -90 and 90"

    with pytest.raises(ValueError) as e:
        Location(0, -181, "London")
    assert str(e.value) == "Coordinate must be between -90 and 90"


def test_should_fail_if_invalid_name():
    with pytest.raises(ValueError) as e:
        Location(51.5074, 0.1278, "")
    assert str(e.value) == "Label must not be empty"

    with pytest.raises(ValueError) as e:
        Location(51.5074, 0.1278, " ")
    assert str(e.value) == "Label must not be empty"

    with pytest.raises(ValueError) as e:
        Location(51.5074, 0.1278, "London!")
    assert str(e.value) == "Label must be alphanumeric"


def test_should_strip_whitespace_from_label():
    location = Location(51.5074, 0.1278, " London  ")
    assert location.label == "London"
