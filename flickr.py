# Modules in standard library
from collections import defaultdict
import xml.etree.ElementTree as ET

# Modules not in standard library
from common import *
import flickrapi

# Get the authenticated Flickr object
flickr = get_flickr()

def get_brands():
    """Get the list of all brands of cameras.

    Returns {camera_id: camera_name, ...}."""

    brands_response = flickr.cameras_getBrands()
    brands_dict = {}
    for b in brands_response.iter('brand'):
        camera_id = b.get('id')
        camera_name = b.get('name')
        brands_dict[camera_id] = camera_name

    return brands_dict

def get_brand_models(brand_id):
    """Get the details of camera models belonging to a given brand.

    Returns {camera_id: {'name': camera_name, 'megapixels':
    megapixels, 'zoom': zoom}, ...}"""

    brand_models_response = flickr.cameras_getBrandModels(brand = brand_id)
    brand_models_dict = {}
    for cam in brand_models_response.iter('camera'):
        camera_id = cam.get('id')
        camera_name = cam.find('name').text

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

        print ("Name = %s, MP = %s, Zoom = %s" % (camera_name, megapixels, zoom)).encode('ascii', errors = 'ignore')

        brand_models_dict[camera_id] = {'name': camera_name,
                                        'megapixels': megapixels,
                                        'zoom': zoom}
    return brand_models_dict
        
def get_brands_models(brands_dict):
    """Get models from all the given brands. The brands should be in
    the dictionary form, as returned by get_brands().

    Returns {brand_id: {camera_id: {'name': camera_name, 'megapixels':
    megapixels, 'zoom': zoom}, ...}, ...}."""

    camera_models_dict = defaultdict(dict)
    for brand_id in brands_dict:
        brand_models = get_brand_models(brand_id)
        for brand in brand_models:
            camera_models_dict[brand_id][brand] = brand_models[brand]

    return camera_models_dict

if __name__ == "__main__":
    # Get all camera brands
    b = get_brands()
    
    # Get all models from each of the brands
    m = get_brands_models(b)
