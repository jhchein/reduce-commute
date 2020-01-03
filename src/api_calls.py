import requests
import json
import os


subscription_key = os.environ.get("SECRETKEY")

def get_metro_id(lat, lon):
    url = f"https://atlas.microsoft.com/mobility/metroArea/id/json?subscription-key={subscription_key}&api-version=1.0&query={lat}, {lon}&queryType=position"

    response = requests.request("GET", url, headers={}, data = {})

    return json.loads(response.text.encode("utf-8"))["results"][0]["metroId"]


def get_position_from_azure_maps(address_line, lat=None, lon=None, radius=None, metro_id=None):
    """Queries a position (lat, lon, metro_id) for a given address. 
    
    If you want to search nearby another location 'search center', you can use 'lat', 'lon' and 'radius' to specify that other location and search radius (m). 
    
    Arguments:
        address_line {str} -- The queried address.
    
    Keyword Arguments:
        lat {float} -- latitude of search center (default: {None})
        lon {float} -- longitude of search center (default: {None})
        metro_id {int} -- Azure Maps Metro Id. Will be required for urban mobility queries (default: {None})
        radius {int} -- Search radius from 'Search Center' (default: {None})
    
    Returns:
        tuple(int, int, int) -- latitude, longitude, metro_id
    """
    url = f"https://atlas.microsoft.com/search/fuzzy/json?subscription-key={subscription_key}&api-version=1.0&query={address_line}"
    
    if lat and lon:
        url += f"&lat={lat}&lon={lon}"
        if radius:
            url += f"&radius={radius}"
    
    print(f"parsing position for '{address_line}'")
    
    response = requests.request("GET", url, headers={}, data={})
    
    position = json.loads(response.text.encode("utf-8"))["results"][0]["position"] # first result from query
    
    if not metro_id:
        metro_id = get_metro_id(position["lat"], position["lon"])
    
    return position["lat"], position["lon"], metro_id


def get_mobility_routes_from_azure_maps(origin_lat, origin_lon, destination_lat, destination_lon, arrival_time="2020-01-06T08:00:00Z", metro_id=3300):
    url = f"https://atlas.microsoft.com/mobility/transit/route/json?subscription-key={subscription_key}&api-version=1.0&metroId={metro_id}&origin={origin_lat}, {origin_lon}&originType=position&destination={destination_lat}, {destination_lon}&destinationType=position&time={arrival_time}&timeType=arrival"

    response = requests.request("GET", url, headers={}, data={})

    try:
        return json.loads(response.text.encode("utf8"))["results"]
    except:
        print(f"Could not parse route.")
        return False

def get_car_routes_from_azure_maps(origin_lat, origin_lon, destination_lat, destination_lon, arrive_at_time="2020-01-06T08:00:00Z"):
    url = f"https://atlas.microsoft.com/route/directions/json?subscription-key={subscription_key}&api-version=1.0&query={origin_lat},{origin_lon}:{destination_lat},{destination_lon}&maxAlternatives=1&computeTravelTimeFor=all&traffic=true&routeType=shortest"

    if arrive_at_time:
        url += f"&arriveAt={arrive_at_time}"

    response = requests.request("GET", url, headers={}, data={})

    try:
        routes = json.loads(response.text.encode("utf8"))["routes"]
        return [route["summary"] for route in routes]
    except:
        print(f"Could not parse route.")
        return False