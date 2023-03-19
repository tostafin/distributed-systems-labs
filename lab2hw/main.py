from statistics import fmean

import requests

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from typing import Annotated

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/weather-data/", response_class=HTMLResponse)
async def submit_form(request: Request, location: Annotated[str, Form()], startdate: Annotated[str, Form()],
                      enddate: Annotated[str, Form()]):
    weather_data = get_weather_data(location, startdate, enddate)
    return templates.TemplateResponse(
        "weather-data.html",
        {"request": request, "temperature_2m": weather_data[0], "relativehumidity_2m": weather_data[1]}
    )


def get_weather_data(location, startdate, enddate):
    location_request = requests.get(f"https://nominatim.openstreetmap.org/search?q={location}&format=jsonv2&limit=1")
    try:
        location_request.raise_for_status()
    except requests.HTTPError:
        print(location_request.json()["message"])

    location_data = location_request.json()
    if not location_data:
        raise ValueError("Location not found. Try again.")

    lat, lon = location_data[0]["lat"], location_data[0]["lon"]

    base_weather_request = f"https://archive-api.open-meteo.com/v1/era5?" \
                           f"latitude={lat}&longitude={lon}&start_date={startdate}&end_date={enddate}&hourly="
    weather_features = [
        "temperature_2m",
        "relativehumidity_2m"
    ]
    weather_request = requests.get(
        base_weather_request + ",".join(weather_features)
    )
    try:
        weather_request.raise_for_status()
    except requests.HTTPError:
        print(weather_request.json()["reason"])

    weather_data = weather_request.json()
    return fmean(weather_data["hourly"]["temperature_2m"]), fmean(weather_data["hourly"]["relativehumidity_2m"])
