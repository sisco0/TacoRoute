import googlemaps
from datetime import datetime
import os
import time
import pandas as pd
from dotenv import load_dotenv
import numpy as np
import itertools
import pprint
import numpy as np
from satsp import solver
import matplotlib.pyplot as plt
import sys
import json
sys.path.append('simulated-annealing-tsp')
from anneal import SimAnneal

def storeDataFrame(partial_dm, oreq, dreq, dfDist, dfTime):
    for oidx, oval in enumerate(partial_dm['rows']):
        for didx, dval in enumerate(oval['elements']):
            dfDist[oreq[oidx]][dreq[didx]] = dval['distance']['value']
            dfTime[oreq[oidx]][dreq[didx]] = dval['duration']['value']

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
    #        radius = 1000,
            keyword = "tacos",
    #        rank_by = "prominence")
            rank_by = "distance")
    results = places['results']
    while len(results) < max_places and 'next_page_token' in places:
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
    dfDist = pd.DataFrame(np.zeros((n,n)))
    dfDist.columns = places_labels
    dfDist.index = places_labels
    dfTime = pd.DataFrame(np.zeros((n,n)))
    dfTime.columns = places_labels
    dfTime.index = places_labels
    # Fill the dataframe
    keys = list(vertex.keys())
    partitions = list(itertools.product(np.array_split(np.array(keys), n//10+1), repeat=2))
    # pprint.pprint(partitions)
    # print('Algorithm:')
    for partition in partitions:
        # print(partition[0])
        # print(partition[1])
        partial_dm = gmaps.distance_matrix(
                [vertex[v]['geometry']['location'] for v in partition[0]],
                [vertex[v]['geometry']['location'] for v in partition[1]])
        # pprint.pprint(partial_dm)
        storeDataFrame(partial_dm, partition[0], partition[1], dfDist, dfTime)
        time.sleep(3)
    dfDist.to_csv('dfDist.csv')
    dfTime.to_csv('dfTime.csv')
    city_list = []
    for idx, v in enumerate(vertex.keys()):
        loc = vertex[v]['geometry']['location']
        city_list.append([loc['lat'], loc['lng']])
    pprint.pprint(city_list)
    saDist = SimAnneal(coords=city_list,dist=dfDist.to_numpy(),alpha=0.999, stopping_iter=1000000)
    saDist.batch_anneal(times=30)
    solidxs = saDist.best_solution
    startidx = list(vertex.keys()).index(starting_vertex['place_id'])
    solidxs = solidxs[solidxs.index(startidx):] + solidxs[0:solidxs.index(startidx)]
    solidxs.append(solidxs[0])
    print(f'https://www.google.com/maps/dir/' + ('/').join([(',').join([str(s) for s in city_list[idx]]) for idx in solidxs]))
    print(f'https://maps.openrouteservice.org/directions?' + 
            'n1=' + str(city_list[solidxs[0]][0]) + 
            '&n2=' + str(city_list[solidxs[0]][1]) +
            '&n3=13' +
            '&a=' + ','.join(','.join([str(s) for s in city_list[idx]]) for idx in solidxs) +
            '&b=0&c=0&k1=en-US&k2=km')
    data = [{'lat': city_list[idx][0], 'lng': city_list[idx][1]} for idx in solidxs]
    with open('saDist.json','w') as write_file:
        json.dump(data, write_file)
    saTime = SimAnneal(coords=city_list,dist=dfTime.to_numpy(),alpha=0.999, stopping_iter=1000000)
    saTime.batch_anneal(times=30)
    solidxs = saTime.best_solution
    solidxs.append(solidxs[0])
    print(f'https://www.google.com/maps/dir/' + ('/').join([(',').join([str(s) for s in city_list[idx]]) for idx in solidxs]))
    print(f'https://maps.openrouteservice.org/directions?' + 
            'n1=' + str(city_list[solidxs[0]][0]) + 
            '&n2=' + str(city_list[solidxs[0]][1]) +
            '&n3=13' +
            '&a=' + ','.join(','.join([str(s) for s in city_list[idx]]) for idx in solidxs) +
            '&b=0&c=0&k1=en-US&k2=km')
