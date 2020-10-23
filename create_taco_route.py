import googlemaps
from datetime import datetime
import os
import time
from dotenv import load_dotenv
import numpy as np

if __name__=='__main__':
    # Load GOOGLE_MAPS_API_KEY from .env file
    load_dotenv(verbose = True)
    # Load the environment variable to memory
    gmaps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    # Configure googlemaps with the API key
    gmaps = googlemaps.Client(key = gmaps_api_key)

    # First, select the first-last vertex for the graph
    # This is accomplished by searching its location
    # by using Google Maps.
    starting_vertex = gmaps.geocode('Universidad Politecnica de Lazaro Cardenas')
    if len(starting_vertex) != 1:
        print('Starting point is not clear')
        exit
    starting_vertex = starting_vertex[0]
    # Search nearby that position within a radius of 3km
    max_places = 20 # Maximum is 60
    places = gmaps.places_nearby(
            location = starting_vertex['geometry']['location'],
            radius = 3000,
            keyword = "tacos",
            rank_by = "prominence")
    results = places['results']
    while len(results) < max_places and 'next_page_token' in places:
        print(places['next_page_token'])
        time.sleep(3)
        places = gmaps.places_nearby(
                page_token = places['next_page_token'])
        results = results + places['results']
    del results[max_places:]
    vertex = dict()
    vertex[starting_vertex['place_id']] = starting_vertex
    for place in results:
        place_id = place['place_id']
        vertex[place_id] = place
    places_labels = vertex.keys()
    locations = [vertex[v]['geometry']['location'] for v in vertex]
    n = len(locations)
    distance_matrix = np.zeros((n,n))
    # Create 5x5 squares
    for k in range(n//5+1):
        # TODO

    # Fill distance_matrix
    distance_matrix_portion = gmaps.distance_matrix(locations, locations)
    print(distance_matrix)

