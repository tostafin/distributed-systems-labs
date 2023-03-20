from typing import Final, List

GEOCODE_API_URL: Final[str] = "https://nominatim.openstreetmap.org/search?q={location}&format=jsonv2&limit=1"
WEATHER_HISTORICAL_DATA_API_URL: Final[str] = "https://archive-api.open-meteo.com/v1/era5?" \
                                              "latitude={latitude}&longitude={longitude}" \
                                              "&start_date={startdate}&end_date={enddate}&{weatherinterval}="
WEATHER_FORECAST_API_URL: Final[str] = "https://api.open-meteo.com/v1/forecast?" \
                                       "latitude={latitude}&longitude={longitude}&forecast_days={forecastdays}" \
                                       "&{weatherinterval}="

WEATHER_INTERVAL: Final[str] = "hourly"
WEATHER_DATES: Final[str] = "time"
WEATHER_UNITS: Final[str] = f"{WEATHER_INTERVAL}_units"
WEATHER_FEATURES: Final[List[str]] = [
    "temperature_2m",
    "relativehumidity_2m"
]
