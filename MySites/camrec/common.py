from collections import defaultdict
import cPickle as pickle

import flickrapi

def get_api_key(fname):
    f = open(fname)
    api_key = f.read().strip()
    f.close()
    return api_key

def get_flickr(key_fname = 'api_key'):
    api_key = get_api_key(key_fname)
    flickr = flickrapi.FlickrAPI(api_key)
    return flickr
    
def default_list_dict():
    return defaultdict(list)

def default_set_dict():
    return defaultdict(set)

def default_int_dict():
    return defaultdict(int)

def default_float_dict():
    return defaultdict(float)
