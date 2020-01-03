import json
import os

from api_calls import get_position_from_azure_maps, get_mobility_routes_from_azure_maps, get_car_routes_from_azure_maps

from statistics import mean

from caching import get_cache, save_cache, cache_defaultdict

from collections import defaultdict

weeks_per_month = 4.38
mean_parking_time = 4*60

def get_car_route_time(address_line_1, address_line_2, max_distance =None, ambiguous=False, arrival_time = "2020-01-06T08:00:00Z"):
    global cache

    
    # try:
    potential_routes = cache["car_routes"][address_line_1][address_line_2][arrival_time]
    # except KeyError:
    if len(potential_routes) < 1:
        if max_distance:
            ambiguous = True

        origin_lat, origin_lon, metro_id = get_position(address_line_1)

        destination_lat, destination_lon, destination_metro_id = get_position(
            address_line_2, lat=origin_lat, lon=origin_lon, radius=max_distance, metro_id=metro_id, ambiguous=ambiguous)
        
        if origin_lat == destination_lat and origin_lon == origin_lon:
            return 0

        print(f"parsing car route from '{address_line_1}' to '{address_line_2}'")
        potential_routes = get_car_routes_from_azure_maps(
            origin_lat, origin_lon, destination_lat, destination_lon, arrive_at_time=arrival_time
        )

        if not potential_routes:
            return False

        # Cache route
        # cache["car_routes"][address_line_1] = cache["car_routes"].get(address_line_1, {})
        # cache["car_routes"][address_line_1][address_line_2] = cache["car_routes"][address_line_1].get(address_line_2, {})
        cache["car_routes"][address_line_1][address_line_2][arrival_time] = potential_routes

    shortest_trip = min(
        [int(route["historicTrafficTravelTimeInSeconds"]) for route in potential_routes]
    )
    return shortest_trip + mean_parking_time

def get_urban_mobility_route_time(address_line_1, address_line_2, ambiguous=False, max_distance=None, arrival_time = "2020-01-06T08:00:00Z"):
    global cache

    potential_routes = cache["urban_mobility_routes"][address_line_1][address_line_2]

    if len(potential_routes) < 1:
        if max_distance:
            ambiguous = True

        origin_lat, origin_lon, metro_id = get_position(address_line_1)

        destination_lat, destination_lon, destination_metro_id = get_position(
            address_line_2, lat=origin_lat, lon=origin_lon, radius=max_distance, metro_id=metro_id, ambiguous=ambiguous)
        
        if origin_lat == destination_lat and origin_lon == origin_lon:
            return 0
    
        print(f"parsing route from '{address_line_1}' to '{address_line_2}'")
        potential_routes = get_mobility_routes_from_azure_maps(
            origin_lat, origin_lon, destination_lat, destination_lon, arrival_time=arrival_time
        )
        if not potential_routes:
            return False

        # Cache route
        cache["urban_mobility_routes"][address_line_1][address_line_2] = potential_routes

    shortest_trip = min(
        [int(route["travelTimeInSeconds"]) for route in potential_routes]
    )
    return shortest_trip


def get_position(address_line, lat=None, lon=None, metro_id=None, radius=None, ambiguous=False):
    global cache

    if not ambiguous and address_line in cache["positions"]:
        return cache["positions"][address_line]

    lat, lon, metro_id = get_position_from_azure_maps(address_line, lat, lon, metro_id, radius) # lat, lon, metro_id

    if not ambiguous:
        cache["positions"][address_line] = lat, lon, metro_id

    return lat, lon, metro_id


def get_shortest_travel_time(origin, appointment_details, fallback_minutes=30, arrival_time=None, car=False, urban_mobility=True):
    destination_addresses = appointment_details["addresses"]
    take_all = appointment_details.get("take_all", False)

    if not take_all and origin in destination_addresses:
        return 0

    ambiguous_locations = appointment_details.get("ambiguous_locations", False)
    arrival_time = appointment_details.get("arrival_time", arrival_time)

    travel_times = []
    if urban_mobility:
        travel_times.extend([get_urban_mobility_route_time(address_line_1=origin,address_line_2=target_adress,ambiguous=ambiguous_locations, arrival_time=arrival_time) for target_adress in destination_addresses])
    if car:
        travel_times.extend([get_car_route_time(address_line_1=origin,address_line_2=target_adress,ambiguous=ambiguous_locations, arrival_time=arrival_time) for target_adress in destination_addresses])
    
    travel_times = [travel_time for travel_time in travel_times if travel_time is not False]

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
    car = typical_week.get("car", False)
    arrival_time = typical_week.get("arrival_time", None)

    for appointment, appointment_details in typical_week["locations"].items():
        times_per_week = appointment_details["times_per_week"]
        car = appointment_details.get("car", typical_week.get("car", False))

        travel_time = get_shortest_travel_time(origin, appointment_details, arrival_time=arrival_time, car=car)

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
    with open("data/typical_week.json", "rb") as fh:
        typical_week = json.load(fh)

    cache = get_cache()
    
    # positions_cache = cache["postions"]
    # urban_mobility_route_cache= cache["urban_mobility_routes"]
    # car_route_cache = cache["car_routes"]

    # PARSE
    result = {}
    for origin in potential_addresses:
        result[origin] = estimate_traveltime_for_address(origin, typical_week)

    with open("data/result.json", "w") as fh:
        json.dump(result, fh, indent=2)

    save_cache(cache)