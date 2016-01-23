#!/usr/bin/env python

# Scrapes a whole city from Flickr.

import argparse, csv, collections, ConfigParser, tqdm, flickr_api
from jinja2 import Environment, PackageLoader, Template
from shapely import geometry
import util
parser = argparse.ArgumentParser()
parser.add_argument('--neighborhoods_file', default='data/sffind_neighborhoods.json')
parser.add_argument('--target_neighborhood', default='Noe Valley')
parser.add_argument('--config_file', default='config.txt')
parser.add_argument('--autotags_file', default='data/autotags.tsv')
parser.add_argument('--num_photos_per_list', type=int, default=10)
parser.add_argument('--participant_id', default='pdemo')
args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read('config.txt')
flickr_api.set_keys(api_key=config.get('flickr', 'api_key'), api_secret=config.get('flickr', 'api_secret'))
# flickr_api.enable_cache()

def convert_autotags_list(autotags_scores):
    """ input: '[dog#0.95,cat#0.85,people#0.99]'. output: ['dog', 'people'] (b/c
    only keeping autotags with scores > .9) """
    if autotags_scores == '' or autotags_scores == '[]':
        return []
    items = autotags_scores.strip('[]').split(',')
    return [item.split('#')[0] for item in items if float(item.split('#')[1])>.9]

def generate_html_gallery(outfile_name, image_filenames):
    """ Renders the gallery.html template so we have a bunch of images in one
    html file. """
    env = Environment(loader=PackageLoader('flickr', 'templates'))
    template = env.get_template('gallery.html')
    outfile = open(outfile_name, 'w')
    outfile.write(template.render(urls=image_filenames))
    outfile.close()

if __name__=='__main__':
    nghds = util.load_neighborhoods(args.neighborhoods_file)
    autotags_file = csv.reader(open(args.autotags_file), delimiter='\t')
    # photo_id, date, date_taken_unknown, lon, lat, tags
    ids_autotags = {} # string -> list of autotags
    for line in autotags_file:
        autotags_list = convert_autotags_list(line[5])
        ids_autotags[line[0]] = autotags_list

    for nghd in nghds:
        if nghd['properties']['name'].lower() == args.target_neighborhood.lower():
            nghd_of_interest = nghd

    nghd_geom = geometry.asShape(nghd_of_interest['geometry'])
    bbox = str([round(b, 6) for b in nghd_geom.bounds])[1:-1]
    # 4-tuple: (min lon, min lat, max lon, max lat). [1:-1] to remove parentheses.
    # recent_photos = flickr_api.Photo.search(bbox=bbox, sort='date-taken-desc')
    recent_photos = flickr_api.Walker(flickr_api.Photo.search, bbox=bbox, sort='date-taken-desc')

    recent_ids_seen = set() # so we get 1 per person
    recent_filenames = []
    for photo in tqdm.tqdm(recent_photos[0:args.num_photos_per_list*10]):
        loc = photo.getLocation()
        point = geometry.Point(loc['longitude'], loc['latitude'])
        if not nghd_geom.contains(point):
            # point is within bounding box but not actually in neighborhood.
            continue
        
        if photo['id'] in ids_autotags:
            autotags = ids_autotags[photo['id']]
        else:
            autotags = []

        if photo['owner']['id'] not in recent_ids_seen:
            recent_ids_seen.add(photo['owner']['id'])
            filename = 'photos/'+args.participant_id+'/recent/'+photo['id']+'.jpg'
            photo.save(filename, size_label = 'Small')
            recent_filenames.append(filename)
        if len(recent_filenames) >= args.num_photos_per_list:
            break
    generate_html_gallery(args.participant_id + "_recent.html", recent_filenames)

    int_photos = flickr_api.Walker(flickr_api.Photo.search, bbox=bbox, sort='interestingness-desc')
    int_ids_seen = set()
    int_filenames = []
    for photo in tqdm.tqdm(int_photos[0:args.num_photos_per_list*10]):
        loc = photo.getLocation()
        point = geometry.Point(loc['longitude'], loc['latitude'])
        if not nghd_geom.contains(point):
            # point is within bounding box but not actually in neighborhood.
            continue
        # autotags = ids_autotags[int(photo['id'])]

        if photo['owner']['id'] not in int_ids_seen:
            int_ids_seen.add(photo['owner']['id'])
            filename = 'photos/'+args.participant_id+'/interesting/'+photo['id']+'.jpg'
            photo.save(filename, size_label = 'Small')
            int_filenames.append(filename)
        if len(int_filenames) >= args.num_photos_per_list:
            break
    generate_html_gallery(args.participant_id + "_interesting.html", int_filenames)


