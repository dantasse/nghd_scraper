#!/usr/bin/env python

# Scrapes a whole city from Yelp.

import argparse, csv, collections, geojson, ConfigParser, time
from yelpapi import YelpAPI
from shapely import geometry
import util
parser = argparse.ArgumentParser()
parser.add_argument('--neighborhoods_file', default='data/sffind_neighborhoods.json')
parser.add_argument('--config_file', default='config.txt')
parser.add_argument('--output_file', default='yelp_results.json')
args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read('config.txt')
yelp_api = YelpAPI(config.get('yelp', 'consumer_key'),
        config.get('yelp', 'consumer_secret'), config.get('yelp', 'token'),
        config.get('yelp', 'token_secret'))

# results = yelp_api.search_query(term='coffee', location='Noe Valley, San Francisco, CA')
# https://www.yelp.com/developers/documentation/v2/search_api
num_results_so_far = 0
while True:
    results = yelp_api.search_query(category_filter='coffee',
        location='San Francisco, CA', offset=num_results_so_far)
    print results['total']
    for business in results['businesses']:
        if business['is_closed']:
            print "Not including, permanently closed: %s" % business['name']
            continue
        print business['name']
        print business['location']['coordinate']

    num_results_so_far += len(results['businesses'])
    if num_results_so_far >= results['total']:
        break
    time.sleep(3)
# results = yelp_api.search_query(category_filter='coffee',
#         location='Noe Valley, San Francisco, CA', offset = 20)
# 
# print results['total']
# for business in results['businesses']:
#     print business['name']
#     print business['location']['coordinate']
