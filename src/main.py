import json
import os

from api_calls import get_position_from_azure_maps, get_routes_from_azure_maps

from statistics import mean

weeks_per_month = 4.38

def get_route_time(address_line_1, address_line_2, ambiguous=False, max_distance=None):
    global route_cache

    if max_distance:
        ambiguous = True

    origin_lat, origin_lon, metro_id = get_position(address_line_1)

    destination_lat, destination_lon, destination_metro_id = get_position(
        address_line_2, lat=origin_lat, lon=origin_lon, radius=max_distance, metro_id=metro_id, ambiguous=ambiguous)
    
    if origin_lat == destination_lat and origin_lon == origin_lon:
        return 0

    try:
        potential_routes = route_cache[address_line_1][address_line_2]
    except KeyError:
        print(f"parsing route from '{address_line_1}' to '{address_line_2}'")
        potential_routes = get_routes_from_azure_maps(
            origin_lat, origin_lon, destination_lat, destination_lon
        )
        if not potential_routes:
            return False

        # Cache route
        route_cache[address_line_1] = route_cache.get(address_line_1, {})
        route_cache[address_line_1][address_line_2] = potential_routes

    shortest_trip = min(
        [int(route["travelTimeInSeconds"]) for route in potential_routes]
    )
    return shortest_trip


def get_position(address_line, lat=None, lon=None, metro_id=None, radius=None, ambiguous=False):
    global positions_cache

    if not ambiguous and address_line in positions_cache:
        return positions_cache[address_line]

    lat, lon, metro_id = get_position_from_azure_maps(address_line, lat, lon, metro_id, radius) # lat, lon, metro_id

    if not ambiguous:
        positions_cache[address_line] = lat, lon, metro_id

    return lat, lon, metro_id


def get_shortest_travel_time(origin, appointment_details, fallback_minutes=30):
    destination_addresses = appointment_details["addresses"]
    take_all = appointment_details.get("take_all", False)
    ambiguous_locations = appointment_details.get("ambiguous_locations", False)

    travel_times = [get_route_time(address_line_1=origin,address_line_2=target_adress,ambiguous=ambiguous_locations) for target_adress in destination_addresses]
    
    try:
        if take_all:
            return mean(travel_times)
        else:
            return min(travel_times)
    except Exception as e:
        print(e)
        print(f"Could find a route from {origin} to {destination_addresses}. Estimating a {fallback_minutes} Minute trip.")
        travel_time = fallback_minutes*60 # Fallback 30 minutes if no address was found.
    return travel_time


def estimate_traveltime_for_address(origin, typical_week):
    traveltimes = {}
    total_travel_time = 0

    for appointment, appointment_details in typical_week.items():
        times_per_week = appointment_details["times_per_week"]

        travel_time = get_shortest_travel_time(origin, appointment_details)

        travel_time_per_month = 2 * times_per_week * travel_time * weeks_per_month / 3600
        total_travel_time += travel_time_per_month
        traveltimes[appointment] = travel_time_per_month

    print(f"Total time per month for '{origin}': {total_travel_time:3.1f} hours")
    traveltimes["total time"] = total_travel_time
    return traveltimes

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)
    os.makedirs("data/viz", exist_ok=True)
    
    # LOAD CONFIGURATION

    with open("data/potential_addresses.json", "rb") as fh:
        potential_addresses = json.load(fh)

    with open("data/reference_locations.json", "rb") as fh:
        reference_locations = json.load(fh)

    with open("data/typical_week.json", "rb") as fh:
        typical_week = json.load(fh)

    # LOADED CACHED LOCATIONS
    try:
        with open("data/cache/positions_cache.json", "r") as fh:
            positions_cache = json.load(fh)
    except FileNotFoundError:
        positions_cache = {}

    try:
        with open("data/cache/route_cache.json", "r") as fh:
            route_cache = json.load(fh)
    except FileNotFoundError:
        route_cache = {}

    # PARSE
    result = {}
    for origin in potential_addresses:
        result[origin] = estimate_traveltime_for_address(origin, typical_week)

    with open("data/result.json", "w") as fh:
        json.dump(result, fh, indent=2)

    # SAVE CACHE
    with open("data/cache/positions_cache.json", "w") as fh:
        json.dump(positions_cache, fh, indent=2)
    with open("data/cache/route_cache.json", "w") as fh:
        json.dump(route_cache, fh, indent=2)
