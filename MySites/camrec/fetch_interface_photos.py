# Modules in standard library
from collections import defaultdict
import xml.etree.ElementTree as ET

# Modules not in standard library
from common import *
from interface import *
import cPickle as pickle
import flickrapi
import shelve

# Get the authenticated Flickr object
flickr = get_flickr()	

def get_10photos(category, camera):
    """Get 10 photo ID from each top camera in each category."""
    photo_10id = []
    f = open("photos_%s_1.dat" % (category), 'r')
    photo_info = pickle.load(f)
    f.close()
    for photo_id in photo_info:
#   for photo_id, photo in photo_info.iteritems():
	if camera == photo_info[photo_id]['exif']['Model'] and len(photo_10id)<10:
#	    print camera
	    photo_10id.append(photo_id)
    return photo_10id

def get_photos(photo_10id):
    """Get the list of tags for each category."""
    photo_sources = []
    for photo_id in photo_10id:
	photos_response = flickr.photos_getSizes(photo_id = int(photo_id))
	sizes = photos_response.find('sizes')
	for size in sizes.iter('size'):
	    if size.get('label')== 'Large Square':
         	source = size.get('source')
		photo_sources.append(source)

#    print photo_sources
    return photo_sources


def collect_interface_photos(n):
    """Collects tags for each category."""
    interface_photos = {}
    top_cameras = get_top_cameras(n)
    for category, cameras in top_cameras.iteritems():
        if (category not in interface_photos):
            interface_photos[category] = {}
	for camera in cameras:
            if (camera not in interface_photos[category]):
                interface_photos[category][camera] = []
	    photo_10id = get_10photos(category, camera[0])
	    photo_sources = get_photos(photo_10id)
	    interface_photos[category][camera] = photo_sources
    print interface_photos
    f = open("interface_photos.dat", 'w')
    pickle.dump(interface_photos, f)
    f.close()



if __name__ == "__main__":

    collect_interface_photos(10)

