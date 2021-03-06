from collections import defaultdict
import xml.etree.ElementTree as ET

from common import *
import fetch_camera_data
import flickrapi

flickr = get_flickr()

def get_photos(tags, sort_order = 'interestingness-desc',
               page = 1, per_page = 10, **kwargs):
    """Search for photos matching a given tag, and return results in a
    dictionary.

    The maximum value of `per_page' is 500.

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
    photo_dict['ncomments'] = comments.text

    photo_dict['tags'] = {}
    for tag in photo.find('tags').iter('tag'):
        tag_id = tag.get('id')
        photo_dict[tag_id] = {'id': tag_id, 'name': tag.text}

    #photo_dict['tags'] = { tag.get('id'): {'id': tag.get('id'), 'name': tag.text} for tag in photo.find('tags').iter('tag') }

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
    
def get_photo_user_comments(photo_id):
	"""Get a dictionary of users who commented on a given photo and the comment's text
	"""
	commentors = []
	
	comments_response = flickr.photos_comments_getList(photo_id = str(photo_id))
	comments = comments_response.find('comments')
	for item in comments.iter('comment'):
		commentor = item.get('author')	
		commentors.append(commentor)
		
	return commentors
		
def get_photo_user_favorites(photo_id):
	"""Get a list of users who favorited a given photo.
	"""
	favorites = []
	
	favorites_response = flickr.photos_getFavorites(photo_id = str(photo_id), per_page = 50) #50 is the maximum results returned per page
	for favorite in favorites_response.iter('person'):
		user_id = favorite.get('nsid')
		favorites.append(user_id)
			
	total_pages = int(favorites_response.find('photo').get('pages'))
	
	for i in range(1,total_pages):
		favorites_response = flickr.photos_getFavorites(photo_id = str(photo_id), page=i, per_page = 50) 		
		for favorite in favorites_response.iter('person'):
			user_id = favorite.get('nsid')
			favorites.append(user_id)

	return favorites

def get_camera_from_database(exif_info, camera_data):
    """Returns the camera from the camera database which matches the
    camera used to take the given photo."""

    try:
        model = exif_info['Model']
    except KeyError:
        return None

    model = model.strip()
    model_lower = model.lower()
    make_and_model_lower = None

    if 'Make' in exif_info:
        make = exif_info['Make'].strip()
        make_and_model = "%s %s" % (make, model)
        make_and_model_lower = make_and_model.lower()

    for camera in camera_data:
        # Exact match
        camera_lower = camera.lower()
        if model_lower == camera_lower:
            exif_info['Model'] = camera
            return camera
        # Make + Model match
        if make_and_model_lower == camera_lower:
            exif_info['Model'] = camera
            return camera

    return None

def get_photo_info_full(photo_id, camera_data = None):

    """Get the complete photo information, given the photo ID."""

    # If no camera information is present, return None
    try:
        exif_info = get_exif_info(photo_id)
        # If invalid camera, return None
        if camera_data is not None:
            print "Checking if camera is valid..."
            camera = get_camera_from_database(exif_info, camera_data)
            print "Done."
            if camera is not None:
                exif_info['Model'] = camera
            else:
                print "No matching camera."
                return None
    except flickrapi.FlickrError:
        return None

    print "Getting photo info for id: %s" % (photo_id)
    photo_info = get_photo_info(photo_id)
    print "Getting comments id: %s" % (photo_id)
    photo_comments = get_photo_user_comments(photo_id)
    print "Getting favorites for id: %s" % (photo_id)
    photo_favorites = get_photo_user_favorites(photo_id)
    print "Done."

    photo_info_full = photo_info.copy()
    photo_info_full['exif'] = exif_info
    photo_info_full['user_comments'] = photo_comments
    photo_info_full['user_favorites'] = photo_favorites

    return photo_info_full

def find_photos_with_tags(tags, nphotos = 10, **kwargs):
    """Given the tags, get a list of photos and the complete information
    for each photo."""

    photo_info = {}

    max_photos_per_page = 500
    photos_collected = 0
    i = 1
    camera_data = fetch_camera_data.retrieve_data('camera')

    while True:
        #try:
        photos = get_photos(tags, page = i, per_page = 500, **kwargs)
        #except:
        #    continue
        for photo_id in photos:
            try:
                photo_info_full = get_photo_info_full(photo_id, camera_data)
            except:
                continue
            print "Photo number: %d" % (photos_collected)
            if photo_info_full is not None:
                photo_info[photo_id] = photo_info_full
                photo_info[photo_id]['category'] = tags
                photos_collected += 1
                if photos_collected == nphotos:
                    return photo_info
            else:
                continue
        i += 1

    return photo_info

def get_users_data(photo_info):
    """Returns the data for each user, given the collected photo
    information."""

    users_data = defaultdict(default_set_dict)
    for photo_id, photo in photo_info.iteritems():
        owner_id = photo['owner']['id']
        camera_model = photo['exif']['Model']
        category = photo['category']
        
        users_data[owner_id]['photos'].add(photo_id)
        users_data[owner_id]['cameras'].add(camera_model)
        users_data[owner_id]['categories'].add(category)

        if 'cameras_by_category' not in users_data[owner_id]:
            users_data[owner_id]['cameras_by_category'] = defaultdict(default_int_dict)
        users_data[owner_id]['cameras_by_category'][category][camera_model] += 1

        for comment_user_id in photo['user_comments']:
            users_data[comment_user_id]['categories'].add(category)
            users_data[comment_user_id]['commented_on'].add(owner_id)

        for fav_user_id in photo['user_favorites']:
            users_data[fav_user_id]['categories'].add(category)
            users_data[fav_user_id]['fav_on'].add(owner_id)

    return users_data
