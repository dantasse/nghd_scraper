#!/usr/bin/env python

# Given a neighborhood geojson file, and a neighborhood name, prints to stdout
# a bounding box of coordinates around it.

import argparse, csv, collections, ConfigParser, tqdm, flickr_api
from jinja2 import Environment, PackageLoader, Template
from shapely import geometry
import util
parser = argparse.ArgumentParser()
parser.add_argument('--neighborhoods_file', default='data/sffind_neighborhoods.json')
parser.add_argument('--target_neighborhood', default='Noe Valley')
parser.add_argument('--whole_city', action='store_true')
args = parser.parse_args()

if __name__ == '__main__': 
    nghds = util.load_neighborhoods(args.neighborhoods_file)
    # photo_id, date, date_taken_unknown, lon, lat, tags

    if args.whole_city:
        city_geom = geometry.asShape(nghds[0]['geometry'])
        
    for nghd in nghds:
        if args.whole_city:
            city_geom = city_geom.union(geometry.asShape(nghd['geometry']))

        if nghd['properties']['name'].lower() == args.target_neighborhood.lower():
            nghd_of_interest = nghd
            nghd_geom = geometry.asShape(nghd_of_interest['geometry'])
            bbox = str([round(b, 6) for b in nghd_geom.bounds])[1:-1]
            print nghd['properties']['name']
            print bbox
 

    if args.whole_city:
        city_bbox = str([round(b, 6) for b in city_geom.bounds])[1:-1]
        print "Whole city bounding box:"
        print city_bbox
