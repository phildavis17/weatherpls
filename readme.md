# weatherpls

Weather, please!

A straightforward CLI tool for getting the weather forecast. Uses the OpenWeatherMap API for weather information and OpenStreetMap Nominatim API for reverse geocoding.

## Use
Accepts four flag arguments:
- **--now** prints the current weather conditions at the specified location
- **--today** prints the overall forecast for the current day
- **--week** prints the overall forecast for the next week, inclduing the current day
- **--hourly** prints the hourly forecast for the next 24 hours

## Caching
weatherpls caches api calls in a json format to improve performance. 
