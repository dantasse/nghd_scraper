#!/usr/bin/env python

# Useful functions used in multiple scrapers.

import argparse, csv, collections, geojson, numpy as np

def bounding_box(points):
    """Given points that are each (lat, lon), returns two points that are the
    lower-left and upper-right points."""
    min_lat, min_lon = np.min(points, axis=0)
    max_lat, max_lon = np.max(points, axis=0)
    return ((min_lat, min_lon), (max_lat, max_lon))

def load_neighborhoods(filename):
    """Load a geojson file. Also puts the value 'name' in the properties.
    So for anything you get back from here you can say nghd['properties']['name'].
    """
    nghds = geojson.load(open(filename))
    for nghd in nghds['features']:
        if 'neighborho' in nghd['properties']:
            nghd['properties']['name'] = nghd['properties']['neighborho']
    return nghds['features']
