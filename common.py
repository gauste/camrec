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
    
