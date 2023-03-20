import secrets
from statistics import fmean
from typing import Annotated
from datetime import datetime

import requests

from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from constants import (GEOCODE_API_URL, WEATHER_HISTORICAL_DATA_API_URL, WEATHER_FORECAST_API_URL,
                       DATE_FORMAT, MIN_DATE, MAX_DATE, MIN_FORECAST_DAYS, MAX_FORECAST_DAYS,
                       WEATHER_INTERVAL, WEATHER_DATES, WEATHER_UNITS, WEATHER_FEATURES, Weather)

app = FastAPI()

security = HTTPBasic()

templates = Jinja2Templates(directory="templates")


def authenticate(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"test"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"test"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password.",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request, credentials: Annotated[HTTPBasicCredentials, Depends(authenticate)]):
    return templates.TemplateResponse(
        "form.html", {
            "request": request,
            "mindate": MIN_DATE,
            "maxdate": MAX_DATE,
            "minforecastdays": MIN_FORECAST_DAYS,
            "maxforecastdays": MAX_FORECAST_DAYS
        }
    )


@app.post("/weather-data", response_class=HTMLResponse)
async def submit_form(request: Request, location: Annotated[str, Form()], startdate: Annotated[str, Form()],
                      enddate: Annotated[str, Form()], forecastdays: Annotated[str, Form()]):
    try:
        validate_data(startdate, enddate, forecastdays)
        weather_data = get_complete_weather_data(location, startdate, enddate, forecastdays)
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
    except HTTPException as exception:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": exception.detail}, status_code=exception.status_code
        )


def validate_data(startdate, enddate, forecastdays):
    try:
        datetime.strptime(startdate, DATE_FORMAT)
        datetime.strptime(enddate, DATE_FORMAT)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dates must be passed in format: {DATE_FORMAT}"
        )
    try:
        forecastdays = int(forecastdays)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Forecast days must be an integer")
    if startdate < MIN_DATE or enddate < MIN_DATE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Dates must be at least {MIN_DATE}")
    if startdate > MAX_DATE or enddate > MAX_DATE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Dates cannot be greater than {MAX_DATE}")
    if enddate <= startdate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"End date must be greater than start date")
    if not MIN_FORECAST_DAYS <= forecastdays <= MAX_FORECAST_DAYS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Forecast days must be a number between {MIN_FORECAST_DAYS} and {MAX_FORECAST_DAYS}"
        )


def get_location(request_url):
    location_request = requests.get(request_url)
    location_data = location_request.json()
    try:
        location_request.raise_for_status()
    except requests.HTTPError:
        raise HTTPException(status_code=location_data["status"], detail=location_data["message"])

    if not location_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Location not found")

    return location_data[0]["lat"], location_data[0]["lon"]


def get_weather_data(request_url):
    weather_request = requests.get(request_url + ",".join(WEATHER_FEATURES))
    weather_data = weather_request.json()
    try:
        weather_request.raise_for_status()
    except requests.HTTPError:
        HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=weather_data["reason"])

    return weather_data


def get_complete_weather_data(location, startdate, enddate, forecastdays):
    latitude, longitude = get_location(GEOCODE_API_URL.format(location=location))
    weather_historical_data = get_weather_data(WEATHER_HISTORICAL_DATA_API_URL.format(
        latitude=latitude, longitude=longitude, startdate=startdate, enddate=enddate, weatherinterval=WEATHER_INTERVAL)
    )
    weather_forecast_data = get_weather_data(WEATHER_FORECAST_API_URL.format(
        latitude=latitude, longitude=longitude, forecastdays=forecastdays, weatherinterval=WEATHER_INTERVAL)
    )
    historical_temperature = weather_historical_data[WEATHER_INTERVAL][WEATHER_FEATURES[0]]
    historical_humidity = weather_historical_data[WEATHER_INTERVAL][WEATHER_FEATURES[1]]
    historical_dates = weather_historical_data[WEATHER_INTERVAL][WEATHER_DATES]

    forecast_temperature = weather_forecast_data[WEATHER_INTERVAL][WEATHER_FEATURES[0]]
    forecast_humidity = weather_forecast_data[WEATHER_INTERVAL][WEATHER_FEATURES[1]]
    forecast_dates = weather_forecast_data[WEATHER_INTERVAL][WEATHER_DATES]

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

        temp_unit=weather_historical_data[WEATHER_UNITS][WEATHER_FEATURES[0]],
        humidity_unit=weather_historical_data[WEATHER_UNITS][WEATHER_FEATURES[1]]
    )
