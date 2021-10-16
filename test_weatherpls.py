import pytest
import weatherpls

def test_get_weather():
    nyc_lat = 40.827232375361085
    nyc_long = -73.9466391392184
    assert weatherpls._get_weather_info_by_coord(nyc_lat, nyc_long)

def test_heading():
    assert weatherpls._parse_compass_heading(5) == "N"
    assert weatherpls._parse_compass_heading(355) == "N"
    assert weatherpls._parse_compass_heading(20) == "NNE"
    assert weatherpls._parse_compass_heading(40) == "NE"
    assert weatherpls._parse_compass_heading(60) == "ENE"
    assert weatherpls._parse_compass_heading(90) == "E"
    assert weatherpls._parse_compass_heading(110) == "ESE"
    assert weatherpls._parse_compass_heading(140) == "SE"
    assert weatherpls._parse_compass_heading(150) == "SSE"
    assert weatherpls._parse_compass_heading(190) == "S"
    assert weatherpls._parse_compass_heading(195) == "SSW"
    assert weatherpls._parse_compass_heading(225) == "SW"
    assert weatherpls._parse_compass_heading(240) == "WSW"
    assert weatherpls._parse_compass_heading(260) == "W"
    assert weatherpls._parse_compass_heading(300) == "WNW"
    assert weatherpls._parse_compass_heading(325) == "NW"
    assert weatherpls._parse_compass_heading(345) == "NNW"

def test_kelvin_conversion():
    assert weatherpls._k_to_f(0) == -459.67
    assert weatherpls._k_to_f(255.372) == 0
    assert weatherpls._k_to_f(273.15) == 32
    assert weatherpls._k_to_f(294.261) == 70
    assert weatherpls._k_to_f(373.15) == 212

def test_mps_to_mph():
    assert weatherpls._mps_to_mph(0) == 0
    assert weatherpls._mps_to_mph(1) == 2.24
    assert weatherpls._mps_to_mph(100) == 223.7

def test_make_ordinal():
    assert weatherpls._make_ordinal(1) == "1st"
    assert weatherpls._make_ordinal(2) == "2nd"
    assert weatherpls._make_ordinal(3) == "3rd"
    assert weatherpls._make_ordinal(4) == "4th"
    assert weatherpls._make_ordinal(0) == "0th"
    assert weatherpls._make_ordinal(11) == "11th"
    assert weatherpls._make_ordinal(12) == "12th"
    assert weatherpls._make_ordinal(13) == "13th"
    assert weatherpls._make_ordinal(14) == "14th"
    assert weatherpls._make_ordinal(10) == "10th"
    assert weatherpls._make_ordinal(112) == "112th"
    assert weatherpls._make_ordinal(-5) == "-5th"