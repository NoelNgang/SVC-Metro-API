import argparse
import sys
import time

import requests

# defining the constants
URL = "http://svc.metrotransit.org/nextrip/{}?format=json"
DIRECTIONS = {
    'south': "Southbound",
    'east': "Eastbound",
    'west': "Westbound",
    'north': "Northbound",

}


def get_route_id(route):
    """
    Function to get the route id from the name passed
    """
    try:
        # calling the URL and getting the /routes endpoint
        resp = requests.get(URL.format("Routes"))
        data = resp.json()
        found = False
        for item in data:
            # checking if string matches
            if route.lower() in item["Description"].lower():  # matching the description
                found = True
                return item["Route"]  # getting the route id

        if not found:
            raise Exception
    except Exception as e:
        print(f"Cannot find route : {route}")
        sys.exit(1)


def get_direction_id(route_id, direction):
    """
    Function to get the direction id.
    """
    available = []
    # replacing the direction with standard value from the constants defined aboce
    if direction.lower() in DIRECTIONS.keys():
        direction = str(DIRECTIONS[direction.lower()])
    try:
        resp = requests.get(URL.format(f"Directions/{route_id}"))
        data = resp.json()
        found = False
        for item in data:
            # checking if string matches
            available.append(item['Text'])
            if direction.lower() in item["Text"].lower():  # matching the description
                found = True
                return item["Value"]  # getting the direction id
        if not found:
            raise Exception
    except Exception as e:
        print(f"Cannot find direction for this route: {direction}")
        sys.exit(1)


def get_stop_id(route_id, direction_id, stop):
    """
    Function to get the stop id from available route and direction
    """
    available = []
    try:
        # now getting the stops with teh routeid and direction id we called for
        url = URL.format(f"Stops/{route_id}/{direction_id}")
        resp = requests.get(url)
        data = resp.json()
        found = False
        for item in data:
            # checking if string matches
            available.append(item['Text'])
            if stop.lower() in item["Text"].lower():  # matching the description
                found = True
                return item["Value"]  # getting the route id

        if not found:
            print(f"Not found... Available stops for this route and direction are: {available}")
            raise Exception
    except Exception as e:
        print(f"Cannot find stop for this route and direction: {stop}")
        sys.exit(1)


def get_time(route_id, direction_id, stop_id):
    """
    Function to get the next available time
    """
    # putting all things together to get the time
    url = URL.format(f"{route_id}/{direction_id}/{stop_id}")
    try:
        resp = requests.get(url)
        data = resp.json()
        if data:
            # getting the first available departure time
            dept_time = data[0]['DepartureTime']
            # converting it to next minutes
            return int((float(dept_time[6:16]) - time.time()) // 60)
        else:
            raise Exception
    except Exception as e:
        print(f"Cannot find time for this route and direction and stop")
        sys.exit(1)


if __name__ == "__main__":
    # print(get_time("901", "1", "TF1"))

    parser = argparse.ArgumentParser()
    parser.add_argument("route")
    parser.add_argument("stop")
    parser.add_argument("direction")
    args = parser.parse_args()

    # firstly getting the route
    route_id = get_route_id(args.route)

    if route_id:
        # then getting the direction
        direction_id = get_direction_id(route_id, args.direction)

    if direction_id:
        # then getting the stop id
        stop_id = get_stop_id(route_id, direction_id, args.stop)

    if stop_id:
        # then finally getting the time
        mins = get_time(route_id, direction_id, stop_id)
        print(f"{mins} minutes.")

# python main.py "METRO Blue Line" "Target Field Station Platform 1" "North"
