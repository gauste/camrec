from collections import defaultdict
import xml.etree.ElementTree as ET

from common import *
import flickrapi

flickr = get_flickr()

def get_photos(tags, sort_order = 'interestingness-desc',
               page = 1, per_page = 10, **kwargs):
    """Search for photos matching a given tag, and return results in a
    dictionary.
    
    The important values in the dictionary are:
    d[photo_id]: photo ID
    d[photo_id]['pos']: rank in the search results, zero-indexed
    d[photo_id]['owner']: ID of the photo's owner
    d[photo_id]['title']: title of the photo
    d[photo_id]['tags']: tags associated with the photo
    d[photo_id]['views']: number of views of the photo"""

    params = kwargs.copy()
    extras = ['tags','views']
    params['extras'] = ",".join(extras)
    params['tags'] = tags
    params['sort'] = sort_order
    params['page'] = page
    params['per_page'] = per_page

    print "Querying for photos with tags: %s" % (tags)
    photos_response = flickr.photos_search(**params)
    photos_dict = {}
    print "Number of photos: %d" % len(list(photos_response.iter('photo')))
    for i, photo in enumerate(photos_response.iter('photo')):
        photo_id = photo.get('id')
        photos_dict[photo_id] = {}
        photos_dict[photo_id]['id'] = photo_id
        photos_dict[photo_id]['pos'] = i
        photos_dict[photo_id]['owner'] = photo.get('owner')
        photos_dict[photo_id]['title'] = photo.get('title')
        for extra in extras:
            photos_dict[photo_id][extra] = photo.get(extra)
            
    return photos_dict
    
def get_photo_info(photo_id):
    """Get information about a particular photo and return it as a
    dictionary. The important values stored in the dictionary are:

    d['id'] : photo ID
    d['owner']['id']: owner ID
    d['title']: photo title
    d['description']: photo description
    d['comments']: number of comments
    
    
    The photo is identified by its photo ID, which can be found from a
    get_photos() query.

    """
     
    photo_response = flickr.photos_getInfo(photo_id = str(photo_id))
    
    photo_dict = {}
    photo = photo_response.find('photo')
    photo_dict['id'] = photo.get('id')
        
    owner = photo.find('owner')
    photo_dict['owner'] = {}
    photo_dict['owner']['id'] = owner.get('nsid')
    photo_dict['owner']['username'] = owner.get('username')
    photo_dict['owner']['location'] = owner.get('location')

    title = photo.find('title')
    photo_dict['title'] = title.text

    description = photo.find('description')
    photo_dict['description'] = description.text

    comments = photo.find('comments')
    photo_dict['comments'] = comments.text

    photo_dict['tags'] = { tag.get('id'): {'id': tag.get('id'), 'name': tag.text}
                          for tag in photo.find('tags').iter('tag') }

    return photo_dict

def get_exif_info(photo_id):
    """Get the EXIF information for a given photo as a dictionary.
    d['photo_id']: photo_id
    d[photo"""

    print "Getting EXIF info for photo with ID: %s" % (photo_id)
    exif_response = flickr.photos_getExif(photo_id = str(photo_id))
    exif_dict = {'photo_id': photo_id}

    photo = exif_response.find('photo')
    for exif in photo.iter('exif'):
        label = exif.get('label')
        value = exif.find('raw').text
        exif_dict[label] = value

    return exif_dict
    
def get_photos_and_exif_info(tags, **kwargs):
    """Get photos matching a given tag and information about the camera
    used to take the photo. Discard photos which do not have camera
    model information.

    """
    photos = get_photos(tags, **kwargs)
    photos_and_exif = {} 
    
    for photo_id in photos: 
        try:
            exif_info = get_exif_info(photo_id) 
            if 'Model' in exif_info:
                photos_and_exif[photo_id] = photos[photo_id]
                photos_and_exif[photo_id]['exif'] = exif_info 
        except flickrapi.FlickrError: 
            # Permission denied 
            pass
                
    return photos_and_exif
