#!/usr/bin/env python

# Scrapes a whole city from Flickr.

import argparse, csv, collections, geojson, ConfigParser, time
import flickr_api
from shapely import geometry
import util
parser = argparse.ArgumentParser()
parser.add_argument('--neighborhoods_file', default='data/sffind_neighborhoods.json')
parser.add_argument('--config_file', default='config.txt')
args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read('config.txt')
flickr_api.set_keys(api_key=config.get('flickr', 'api_key'), api_secret=config.get('flickr', 'api_secret'))

nghds = util.load_neighborhoods(args.neighborhoods_file)

# photo = flickr_api.Photo.search(id=23719973823)
# photos = flickr_api.Photo.getRecent()
# for photo in photos:
#     print photo
#     for tag in photo.getInfo()['tags']:
#         print tag
    
# exit()
for nghd in nghds:
    nghd_geom = geometry.asShape(nghd['geometry'])
    bbox = nghd_geom.bounds # 4-tuple: (min lon, min lat, max lon, max lat)
    if nghd['properties']['name']=='Noe Valley':
        photos = flickr_api.Photo.search(bbox=str(bbox)[1:-1])
        for photo in photos:
            loc = photo.getLocation()
            point = geometry.Point(loc['longitude'], loc['latitude'])
            if not nghd_geom.contains(point):
                # point is within convex hull but not actually in neighborhood.
                continue
            print photo['id']
            info = photo.getInfo()
            print info['tags']
            for tag in info['tags']: # argh no autotags here.
                print tag['id']
                print tag['text']
                # print tag.getRelated()
            # print photo.getPhotoUrl()
            # print photo.getPhotoFile()
            # photo.save(photo['id'] + '.jpg') # this actually downloads the photo
            # photo.save(photo['id'] + '.jpg', 'Medium') # saves 500px version
            # TODO: get autotags... argh damn it's not part of Tags


 



