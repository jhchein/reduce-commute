import json
import os

from api_calls import get_position_from_azure_maps, get_routes_from_azure_maps

weeks_per_month = 4.38


def get_route_time(address_line_1, address_line_2, nearby=False):
    global route_cache

    origin_position = get_position(address_line_1)

    if nearby:
        lat, lon = origin_position.split(",")
        destination_position = get_position_from_azure_maps(
            address_line_2, lat=lat, lon=lon.strip()
        )
    else:
        destination_position = get_position(address_line_2)

    if origin_position == destination_position:
        return 0

    try:
        # Try to find cached values
        potential_routes = route_cache[address_line_1][address_line_2]
    except KeyError:
        # Query from Azure maps
        potential_routes = get_routes_from_azure_maps(
            origin_position, destination_position
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


def get_position(address_line):
    global positions_cache

    if address_line in positions_cache:
        return positions_cache[address_line]

    position = get_position_from_azure_maps(address_line)

    positions_cache[address_line] = position
    return position


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    # LOAD CONFIGURATION

    with open("data/potential_addresses.json", "rb") as fh:
        potential_addresses = json.load(fh)

    with open("data/reference_locations.json", "rb") as fh:
        reference_locations = json.load(fh)

    with open("data/typical_week.json", "rb") as fh:
        typical_week = json.load(fh)

    # LOADED CACHED LOCATIONS
    try:
        with open("data/positions_cache.json", "r") as fh:
            positions_cache = json.load(fh)
    except FileNotFoundError:
        positions_cache = {}

    try:
        with open("data/route_cache.json", "r") as fh:
            route_cache = json.load(fh)
    except FileNotFoundError:
        route_cache = {}

    # PARSE
    result = {}
    for origin in potential_addresses:
        # Initiate result entry
        result[origin] = {}
        total_travel_time = 0

        for agenda_point, times_per_week in typical_week.items():
            target_adresses = reference_locations[agenda_point]  # Lookup adresses
            nearby = (
                True if agenda_point in ["Cafe"] else False
            )  # Lookup some locations (cafes) near the origin

            route_times = [
                get_route_time(origin, target_adress, nearby)
                for target_adress in target_adresses
            ]
            route_times = [
                route_time for route_time in route_times if route_time
            ]  # Drop empty entries
            travel_time = min(route_times) if len(route_times) > 0 else 1200
            travel_time_per_month = (
                2 * times_per_week * travel_time * weeks_per_month / 3600
            )
            total_travel_time += travel_time_per_month
            result[origin][agenda_point] = travel_time_per_month
        print(f"Total time per month for '{origin}': {total_travel_time:3.1f} hours")
        result[origin]["total time"] = total_travel_time

    with open("data/result.json", "w") as fh:
        json.dump(result, fh, indent=2)

    # SAVE CACHE
    with open("data/positions_cache.json", "w") as fh:
        json.dump(positions_cache, fh, indent=2)
    with open("data/route_cache.json", "w") as fh:
        json.dump(route_cache, fh, indent=2)
