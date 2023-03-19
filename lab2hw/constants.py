from typing import Final

GEOCODE_API_URL: Final[str] = "https://nominatim.openstreetmap.org/search?q={location}&format=jsonv2&limit=1"
WEATHER_HISTORICAL_DATA_API_URL: Final[str] = "https://archive-api.open-meteo.com/v1/era5?" \
                                              "latitude={latitude}&longitude={longitude}" \
                                              "&start_date={startdate}&end_date={enddate}&hourly="
WEATHER_FORECAST_API_URL: Final[str] = "https://api.open-meteo.com/v1/forecast?" \
                                       "latitude={latitude}&longitude={longitude}&forecast_days={forecastdays}&hourly="

WEATHER_FEATURES = [
    "temperature_2m",
    "relativehumidity_2m"
]
