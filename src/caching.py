import json
import pickle

from collections import defaultdict


def cache_defaultdict():
    """Creates a defaultdict with default type dict
    
    Returns:
        defaultdict -- defaultdict with default type dict
    """
    return defaultdict(cache_defaultdict)


# cache = cache_defaultdict() # defaultdict with default type dict


def get_cache():
    try:
        with open("data/cache/cache.pckl", "rb") as fh:
            cache = pickle.load(fh)
    except FileNotFoundError:
        print("no cache found, creating new cache")
        cache = cache_defaultdict()

    # try:
    #     with open("data/cache/positions_cache.json", "r") as fh:
    #         positions_cache = json.load(fh)
    # except FileNotFoundError:
    #     positions_cache = {}

    # try:
    #     with open("data/cache/urban_mobility_route_cache.json", "r") as fh:
    #         urban_mobility_route_cache = json.load(fh)
    # except FileNotFoundError:
    #     urban_mobility_route_cache = {}

    # try:
    #     with open("data/cache/car_route_cache.json", "r") as fh:
    #         car_route_cache = json.load(fh)
    # except FileNotFoundError:
    #     car_route_cache = {}

    # cache["deprecated"]["postions"] = positions_cache
    # cache["deprecated"]["urban_mobility_routes"] = urban_mobility_route_cache
    # cache["deprecated"]["car_routes"] = car_route_cache

    return cache


def save_cache(cache):
    # print("saving positions cache")
    # with open("data/cache/positions_cache.json", "w") as fh:
    #     json.dump(cache["deprecated"]["positions"], fh, indent=2)

    # print("saving public transport cache")
    # with open("data/cache/urban_mobility_route_cache.json", "w") as fh:
    #     json.dump(cache["deprecated"]["urban_mobility_routes"], fh, indent=2)

    # print("saving car routes cache")
    # with open("data/cache/car_route_cache.json", "w") as fh:
    #     json.dump(cache["deprecated"]["car_routes"], fh, indent=2)

    print("storing caching data")
    with open("data/cache/cache.pckl", "wb") as fh:
        pickle.dump(cache, fh)


def convert_deprecated_cache():
    try:
        with open("data/cache/cache.pckl", "rb") as fh:
            cache = pickle.load(fh)
    except FileNotFoundError:
        cache = cache_defaultdict()

    try:
        with open("data/cache/positions_cache.json", "r") as fh:
            positions_cache = json.load(fh)
    except FileNotFoundError:
        positions_cache = {}

    try:
        with open("data/cache/urban_mobility_route_cache.json", "r") as fh:
            urban_mobility_route_cache = json.load(fh)
    except FileNotFoundError:
        urban_mobility_route_cache = {}

    try:
        with open("data/cache/car_route_cache.json", "r") as fh:
            car_route_cache = json.load(fh)
    except FileNotFoundError:
        car_route_cache = {}

    for address, position in positions_cache.items():
        cache["positions"][address] = position

    for origin, destination_dict in urban_mobility_route_cache.items():
        for destination, routes in destination_dict.items():
            cache["urban_mobility_routes"][origin][destination] = routes

    for origin, destination_dict in car_route_cache.items():
        for destination, time_dict in destination_dict.items():
            for arrival_time, routes in time_dict.items():
                cache["car_routes"][origin][destination][arrival_time] = routes

    save_cache(cache)


if __name__ == "__main__":
    # convert_deprecated_cache()
    cache = get_cache()
    print(cache.keys())
    print(type(cache["car_routes"]))
