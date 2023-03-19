# import requests
#
# city = "Warszawa"
# city_request = requests.get(f"https://nominatim.openstreetmap.org/search?q={city}&format=jsonv2&limit=1")
# try:
#     city_request.raise_for_status()
# except requests.HTTPError:
#     print(city_request.json()["message"])
#
# city_data = city_request.json()
# if not city_data:
#     raise ValueError("No city found. Try again.")
#
# lat, lon = city_data[0]["lat"], city_data[0]["lon"]
#
# weather_request = requests.get(f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lon}&start_date=2021-01-01&end_date=2021-12-31")
# try:
#     city_request.raise_for_status()
# except requests.HTTPError:
#     print(weather_request.json()["reason"])
#
# weather_data = weather_request.json()
# print(weather_data)
