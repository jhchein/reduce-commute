import requests
import json
import os


subscription_key = os.environ.get("SECRETKEY")


def get_position_from_azure_maps(address_line, lat=None, lon=None):
    url = f"https://atlas.microsoft.com/search/fuzzy/json?subscription-key={subscription_key}&api-version=1.0&query={address_line}"
    if lat and lon:
        url += f"&lat={lat}&lon={lon}"
    print(f"parsing position for '{address_line}'")
    response = requests.request("GET", url, headers={}, data={})
    position = json.loads(response.text.encode("utf-8"))["results"][0]["position"]
    return str(f'{position["lat"]}, {position["lon"]}')


def get_routes_from_azure_maps(
    origin, destination, time="2020-01-06T08:00:00Z", metro_id=3300
):
    url = f"https://atlas.microsoft.com/mobility/transit/route/json?subscription-key={subscription_key}&api-version=1.0&metroId={metro_id}&origin={origin}&originType=position&destination={destination}&destinationType=position&time={time}&timeType=arrival"

    print(f"parsing route from {origin} to {destination}")
    response = requests.request("GET", url, headers={}, data={})

    try:
        return json.loads(response.text.encode("utf8"))["results"]
    except:
        # print(f"Could not parse route from '{origin} to {destination}")
        return False
