# Main file which invokes code from fetch_photo_data to aggregate data
# from multiple photo categories.

from common import *
from fetch_photo_data import *
import cPickle as pickle

def collect_data(categories, nphotos):
    """Collects data for `nphotos' number of photos from each category."""

    photo_info = {}
    for category in categories[:3]:
        photo_info_category = find_photos_with_tags(category, nphotos = nphotos)
        f = open("photos_%s_1.dat" % (category), 'w')
        pickle.dump(photo_info_category, f)
        f.close()

        for photo_id, photo in photo_info_category.iteritems():
            if photo_id not in photo_info:
                photo_info[photo_id] = photo

    f = open("photos_all.dat", 'w')
    pickle.dump(photo_info, f)
    f.close()

    users_data = get_users_data(photo_info)
    f = open("users_all.dat", 'w')
    pickle.dump(users_data, f)
    f.close()

    return photo_info, users_data

if __name__ == "__main__":
    categories = ["wildlife", "technology", "people", "nature", "art", "food", "cars", "landscape", "architecture"]
    nphotos = 5

    photo_info, users_data = collect_data(categories, nphotos)
