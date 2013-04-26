# Main file which invokes code from fetch_photo_data to aggregate data
# from multiple photo categories.

from common import *
from fetch_photo_data import *
import cPickle as pickle
import os

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

def combine_data(dirname = 'data'):
    """Combines data from all the photos_*_1.dat files into one photo_all_1.dat file."""
    
    current_dir = os.getcwd()
    os.chdir(dirname)
    photo_info_combined = {}
    print "Combining photo information..."
    for fname in os.listdir('.'):
        print "Fname = ", fname
        if fname.find('photos_') == -1:
            continue

        print "File name: ", fname
        f = open(fname, 'r')
        photo_info = pickle.load(f)
        f.close()

        print "Length of photo info = ", len(photo_info)

        for photo_id, photo in photo_info.iteritems():
            if photo_id not in photo_info_combined:
                photo_info_combined[photo_id] = photo

    print "Dumping..."
    os.chdir(current_dir)
    f = open('photos_all_1.dat', 'wb')
    pickle.dump(photo_info_combined, f)
    f.close()
    print "Done."

    print "Combining user information..."
    users_data = get_users_data(photo_info_combined)
    f = open('users_all_1.dat', 'wb')
    pickle.dump(users_data, f)
    f.close()
    print "Done."


    return photo_info_combined, users_data

def load_data(photos_data_fname = "photos_all.dat", users_data_fname = "users_all.dat"):
    """Loads the data from the saved files."""
    f = open(photos_data_fname)
    photo_info = pickle.load(f)
    f.close()

    f = open(users_data_fname)
    users_data = pickle.load(f)
    f.close()

    return photo_info, users_data

if __name__ == "__main__":
    categories = ["wildlife", "technology", "people", "nature", "art", "food", "cars", "landscape", "architecture"]
    nphotos = 5

    #photo_info, users_data = collect_data(categories, nphotos)
    photo_info, users_data = load_data("photos_wildlife.dat", "users_wildlife.dat")
