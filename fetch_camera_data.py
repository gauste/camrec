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

def get_brands():
    """Get the list of all brands of cameras.

    Returns {brand_id: brand_name, ...}."""

    brands_response = flickr.cameras_getBrands()
    brands_dict = {}
    for b in brands_response.iter('brand'):
        brand_id = b.get('id')
        brand_name = b.get('name')
        brands_dict[brand_id] = brand_name

    return brands_dict

def get_camera_models_by_brand(brand_id, brand_name):
    """Get the details of camera models belonging to a given brand.

    Returns {camera_name: {'brand': brand_name, 'megapixels':
    megapixels, 'zoom': zoom}, 'lcd': size, 'memory_type': memory_type}"""

    brand_models_response = flickr.cameras_getBrandModels(brand = brand_id)
    brand_models_dict = {}
    for cam in brand_models_response.iter('camera'):
        camera_name = cam.find('name').text.encode('ascii', errors = 'ignore')

        # Some cameras have incomplete or no details, assign default
        # values of zero
        details = cam.find('details')
        try:
            megapixels = details.find('megapixels').text
        except AttributeError:
            megapixels = '0'
        try:
            zoom = details.find('zoom').text
        except AttributeError:
            zoom = '0'
        try:
            lcd = details.find('lcd_screen_size').text
        except AttributeError:
            lcd = '0'
        try:
            memory_type = details.find('memory_type').text
        except AttributeError:
            memory_type = '0'
        print ("Name = %s, MP = %s, Zoom = %s" % (camera_name, megapixels, zoom)).encode('ascii', errors = 'ignore')

        brand_models_dict[camera_name] = {'brand': brand_name,
                                      	  'megapixels': megapixels,
                                          'zoom': zoom,
                                          'lcd': lcd,
                                          'memory_type': memory_type}
    return brand_models_dict
        
def get_camera_models(brands_dict):
    """Get models from all the given brands. The brands should be in
    the dictionary form, as returned by get_brands().

    Returns {camera_name: {'brand': brand_name, 'megapixels':
    megapixels, 'zoom': zoom},...}."""

    camera_models_dict = defaultdict(dict)
    for brand_id, brand_name in brands_dict.items():
        camera_models_by_brand = get_camera_models_by_brand(brand_id, brand_name)
        for camera_name, values in camera_models_by_brand.items():
            camera_models_dict[camera_name] = values

    return camera_models_dict

def get_data(filename):
    #Get all camera brands
    b = get_brands()
    
    #Get all models from each of the brands
    m = get_camera_models(b)
        
    #s = shelve.open(filename)
    f = open(filename, 'wb')
    pickle.dump(m,f)
    f.close()

    # try:
    # 	for camera_name, values in m.items():
    # 		s[camera_name] = values
    # 	print len(s)
    # finally:
    # 	s.close()

def retrieve_data(filename):
    f = open(filename, 'r')
    m = pickle.load(f)
    f.close()

    return m
    # s = shelve.open(filename)
    # try:
    # 	for camera_name in s.keys():
    # 		print camera_name, s[camera_name]['brand'], s[camera_name]['megapixels'], s[camera_name]['zoom'], s[camera_name]['lcd'], s[camera_name]['memory_type']
    # 	print len(s)
    # finally:
    # 	s.close()
	
if __name__ == "__main__":
    filename = "camera"
    get_data(filename)
    m = retrieve_data(filename)
