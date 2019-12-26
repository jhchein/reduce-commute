import requests
import json
import os


subscription_key = os.environ.get("SECRETKEY")

def get_metro_id(lat, lon):
    url = f"https://atlas.microsoft.com/mobility/metroArea/id/json?subscription-key={subscription_key}&api-version=1.0&query={lat}, {lon}&queryType=position"

    response = requests.request("GET", url, headers={}, data = {})
    return json.loads(response.text.encode("utf-8"))["results"][0]["metroId"]


def get_position_from_azure_maps(address_line, lat=None, lon=None, metro_id=None,radius=None):
    url = f"https://atlas.microsoft.com/search/fuzzy/json?subscription-key={subscription_key}&api-version=1.0&query={address_line}"
    
    if lat and lon:
        url += f"&lat={lat}&lon={lon}"
        if radius:
            url += f"&radius={radius}"
    
    print(f"parsing position for '{address_line}'")
    
    response = requests.request("GET", url, headers={}, data={})
    
    position = json.loads(response.text.encode("utf-8"))["results"][0]["position"]
    lat, lon = position["lat"], position["lon"]
    
    if not metro_id:
        metro_id = get_metro_id(lat, lon)
    
    return lat, lon, metro_id


def get_routes_from_azure_maps(origin_lat, origin_lon, destination_lat, destination_lon, time="2020-01-06T08:00:00Z", metro_id=3300):
    url = f"https://atlas.microsoft.com/mobility/transit/route/json?subscription-key={subscription_key}&api-version=1.0&metroId={metro_id}&origin={origin_lat}, {origin_lon}&originType=position&destination={destination_lat}, {destination_lon}&destinationType=position&time={time}&timeType=arrival"

    response = requests.request("GET", url, headers={}, data={})

    try:
        return json.loads(response.text.encode("utf8"))["results"]
    except:
        print(f"Could not parse route.")
        return False
