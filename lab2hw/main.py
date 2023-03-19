from statistics import fmean
from typing import Annotated
from dataclasses import dataclass

import requests

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from constants import GEOCODE_API_URL, WEATHER_HISTORICAL_DATA_API_URL, WEATHER_FORECAST_API_URL, WEATHER_FEATURES

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@dataclass
class Weather:
    historical_avg_temp: float
    historical_max_temp: float
    historical_max_temp_date: str
    historical_min_temp: float
    historical_min_temp_date: str

    historical_avg_humidity: float
    historical_max_humidity: float
    historical_max_humidity_date: str
    historical_min_humidity: float
    historical_min_humidity_date: str

    forecast_avg_temp: float
    forecast_max_temp: float
    forecast_max_temp_date: str
    forecast_min_temp: float
    forecast_min_temp_date: str

    forecast_avg_humidity: float
    forecast_max_humidity: float
    forecast_max_humidity_date: str
    forecast_min_humidity: float
    forecast_min_humidity_date: str

    temp_unit: str
    humidity_unit: str


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/weather-data/", response_class=HTMLResponse)
async def submit_form(request: Request, location: Annotated[str, Form()], startdate: Annotated[str, Form()],
                      enddate: Annotated[str, Form()], forecastdays: Annotated[str, Form()]):
    weather_data = get_data(location, startdate, enddate, forecastdays)
    return templates.TemplateResponse(
        "weather-data.html",
        {
            "request": request,

            "historical_avg_temp": weather_data.historical_avg_temp,
            "historical_max_temp": weather_data.historical_max_temp,
            "historical_max_temp_date": weather_data.historical_max_temp_date,
            "historical_min_temp": weather_data.historical_min_temp,
            "historical_min_temp_date": weather_data.historical_min_temp_date,

            "historical_avg_humidity": weather_data.historical_avg_humidity,
            "historical_max_humidity": weather_data.historical_max_humidity,
            "historical_max_humidity_date": weather_data.historical_max_humidity_date,
            "historical_min_humidity": weather_data.historical_min_humidity,
            "historical_min_humidity_date": weather_data.historical_min_humidity_date,

            "forecast_avg_temp": weather_data.forecast_avg_temp,
            "forecast_max_temp": weather_data.forecast_max_temp,
            "forecast_max_temp_date": weather_data.forecast_max_temp_date,
            "forecast_min_temp": weather_data.forecast_min_temp,
            "forecast_min_temp_date": weather_data.forecast_min_temp_date,

            "forecast_avg_humidity": weather_data.forecast_avg_humidity,
            "forecast_max_humidity": weather_data.forecast_max_humidity,
            "forecast_max_humidity_date": weather_data.forecast_max_humidity_date,
            "forecast_min_humidity": weather_data.forecast_min_humidity,
            "forecast_min_humidity_date": weather_data.forecast_min_humidity_date,

            "temp_unit": weather_data.temp_unit,
            "humidity_unit": weather_data.humidity_unit
        }
    )


def get_location(request_url):
    location_request = requests.get(request_url)
    try:
        location_request.raise_for_status()
    except requests.HTTPError:
        print(location_request.json()["message"])

    location_data = location_request.json()
    if not location_data:
        raise ValueError("Location not found. Try again.")

    return location_data[0]["lat"], location_data[0]["lon"]


def get_weather_data(request_url):
    weather_request = requests.get(request_url + ",".join(WEATHER_FEATURES))
    try:
        weather_request.raise_for_status()
    except requests.HTTPError:
        print(weather_request.json()["reason"])

    return weather_request.json()


def get_data(location, startdate, enddate, forecastdays):
    latitude, longitude = get_location(GEOCODE_API_URL.format(location=location))
    weather_historical_data = get_weather_data(WEATHER_HISTORICAL_DATA_API_URL.format(
        latitude=latitude, longitude=longitude, startdate=startdate, enddate=enddate)
    )
    weather_forecast_data = get_weather_data(WEATHER_FORECAST_API_URL.format(
        latitude=latitude, longitude=longitude, forecastdays=forecastdays)
    )
    historical_temperature = weather_historical_data["hourly"]["temperature_2m"]
    historical_humidity = weather_historical_data["hourly"]["relativehumidity_2m"]
    historical_dates = weather_historical_data["hourly"]["time"]

    forecast_temperature = weather_forecast_data["hourly"]["temperature_2m"]
    forecast_humidity = weather_forecast_data["hourly"]["relativehumidity_2m"]
    forecast_dates = weather_forecast_data["hourly"]["time"]

    return Weather(
        historical_avg_temp=round(fmean(historical_temperature), 2),
        historical_max_temp=round(max(historical_temperature), 2),
        historical_max_temp_date=historical_dates[
            max(range(len(historical_temperature)), key=historical_temperature.__getitem__)],
        historical_min_temp=round(min(historical_temperature), 2),
        historical_min_temp_date=historical_dates[
            min(range(len(historical_temperature)), key=historical_temperature.__getitem__)],

        historical_avg_humidity=round(fmean(historical_humidity), 2),
        historical_max_humidity=round(max(historical_humidity), 2),
        historical_max_humidity_date=historical_dates[
            max(range(len(historical_humidity)), key=historical_humidity.__getitem__)],
        historical_min_humidity=round(min(historical_humidity), 2),
        historical_min_humidity_date=historical_dates[
            min(range(len(historical_humidity)), key=historical_humidity.__getitem__)],

        forecast_avg_temp=round(fmean(forecast_temperature), 2),
        forecast_max_temp=round(max(forecast_temperature), 2),
        forecast_max_temp_date=forecast_dates[
            max(range(len(forecast_temperature)), key=forecast_temperature.__getitem__)],
        forecast_min_temp=round(min(forecast_temperature), 2),
        forecast_min_temp_date=forecast_dates[
            min(range(len(forecast_temperature)), key=forecast_temperature.__getitem__)],

        forecast_avg_humidity=round(fmean(forecast_humidity), 2),
        forecast_max_humidity=round(max(forecast_humidity), 2),
        forecast_max_humidity_date=forecast_dates[
            max(range(len(forecast_humidity)), key=forecast_humidity.__getitem__)],
        forecast_min_humidity=round(min(forecast_humidity), 2),
        forecast_min_humidity_date=forecast_dates[
            min(range(len(forecast_humidity)), key=forecast_humidity.__getitem__)],

        temp_unit=weather_historical_data["hourly_units"]["temperature_2m"],
        humidity_unit=weather_historical_data["hourly_units"]["relativehumidity_2m"]
    )
