"""Stores configuration variables for WeatherPls"""

# The default latitude if none is specified
DEFAULT_LAT = 40.8363

# The default longitude if none is specified
DEFAULT_LONG = -73.9358

# The default units to use in the weather report
#  - For Farenheit and miles per hour, use 'imperial'
#  - For Celcius and meters per second, use 'metric'
#  - For Kelvin and meters per second, use 'standard'
#
#  N.B.: This is subject to change with the OpenWeatherMap API.
#        At time of writing, information can be found at: https://openweathermap.org/api/one-call-api#data
DEFAULT_UNITS = "imperial"
