# Modules in standard library
from collections import defaultdict
import xml.etree.ElementTree as ET

# Modules not in standard library
from common import *
import cPickle as pickle
import flickrapi
import shelve

# Get the authenticated Flickr object
flickr = get_flickr()	

def get_categorytags(category):
    """Get the list of tags for each category."""

    tags_response = flickr.tags_getClusters(tag = category)
    tags = []
    clusters = tags_response.find('clusters')
    for cluster in clusters.iter('cluster'):
	for item in cluster:
            tag = item.text
            tags.append(tag)

    print tags
    return tags


def collect_tags(category):
    """Collects tags for each category."""

    tags_info = {}
    tags_info_category = get_categorytags(category)
    f = open("tags_%s_1.dat" % (category), 'w')
    pickle.dump(tags_info_category, f)
    f.close()


if __name__ == "__main__":
    category = "nature"
    #category = ["wildlife", "technology", "people", "nature", "art", "food", "cars", "landscape", "architecture"]
    get_categorytags(category)
    #collect_tags(category)

