import datetime

from common import *
from fetch_photo_data import *
from fractions import Fraction

def parse_time(photo_info):
    """Returns the time the photo was taken using the date string, or None
    if no valid date string is present.
    """
    # Example of date string: 2012:03:19 17:18:57

    if 'Date and Time (Original)' not in photo_info['exif']:
        return None

    taken_time_string = photo_info['exif']['Date and Time (Original)']
    try:
        taken_time = datetime.datetime.strptime(taken_time_string,
                                                "%Y:%m:%d %H:%M:%S").time()
    except ValueError:
        return None

    return taken_time

def generate_category_photo_data(photo_info = None):
    """Given a list of photos, group them by category and store only a
    small set of key-value pairs."""

    if photo_info is None:
        f = open('photos_all_1.dat', 'r')
        photo_info = pickle.load(f)
        f.close()

    category_photo_info = defaultdict(list)
    for photo_id, photo in photo_info.iteritems():
        category = photo['category']
        keys = ['Flash', 'Focal Length', 'Exposure', 'Exposure Mode', 'Aperture', 'White Balance', 'Date and Time (Original)']
        exif = {}
        for key in keys:
            try:
                exif[key] = photo['exif'][key]
            except:
                continue

        category_photo_info[category].append(exif)

    return category_photo_info

def load_category_photo_data(fname = 'category_photo_map.dat'):
    f = open(fname, 'r')
    category_photo_data = pickle.load(f)
    f.close()

    return category_photo_data

def analyze_all_photos(photos):
    """Analyze photos and return a small set of useful properties and the
    distribution of values among the photos."""

    photos_properties = {}
    photos_stats = {}
    for photo_id, photo_info in photos.iteritems():
        photos_properties[photo_id] = {}
        exif_info = photo_info['exif']
        photo_time = parse_time(photo_info)

        if photo_time is not None:
            photos_properties[photo_id]['Time'] = photo_time

        info_keys = ['Flash', 'Focal Length', 'Exposure', 'Exposure Mode', 'Aperture', 'White Balance']
        for key in info_keys:
            if key in exif_info:
                if key not in photos_stats:
                    photos_stats[key] = defaultdict(int)
                value = exif_info[key]
                photos_properties[photo_id][key] = value
                photos_stats[key][value] += 1

    return photos_properties, photos_stats

def analyze_photos(category_photo_info, **kwargs):
    """Analyze photos and return a small set of useful properties and the
    distribution of values among the photos.

    Arguments should be of the form: category = weight."""

    photos_stats = defaultdict(default_float_dict)
    total_weight = 0.0
    for category in kwargs.keys():
        weight = kwargs[category]
        if weight <= 0.001:
            del kwargs[category]
            continue
        print "category = ", category, " weight = ", weight
        total_weight += weight

    for category in kwargs:
        weight = kwargs[category] * 1.0 / total_weight
        print "category = %s, org weight = %s, total weight = %s, new weight = %s" % (category, kwargs[category], total_weight, weight)
        for photo in category_photo_info[category]:
            for key, value in photo.iteritems():
                photos_stats[key][value] += weight
                
        print photos_stats['Aperture']

    return photos_stats

def aggregate_plot_data(data, n_bars = 6, units = ''):
    # Data is in the form: [(value, number of photos with this value), ...]
    length = len(data)
    per_bar = length / n_bars
    bars = []
    ticks = []
    i = 0
    print "length = %d, per_bar = %d, nbars = %d"  % (length, per_bar, n_bars)
    for b in range(n_bars):
        print "min bar index = ", i
        bars.append(0)
        min_bar = data[i][0]
        j_min = i
        if b == n_bars - 1:
            j_max = length
        else:
            j_max = j_min + int(per_bar)

        for j in range(j_min, j_max):
            #bars.append(data[j])
            bars[b] += data[j][1]
        i = j + 1
        print "max bar index = ", i - 1
        max_bar = data[i - 1][0]
        if units != '':
            ticks.append("%s %s - %s %s" % (min_bar, units, max_bar, units))
        else:
            ticks.append("%s - %s" % (min_bar, max_bar))

    print "var s1 = %s;" % (bars)
    print "var ticks = %s;" % (ticks)
    return bars, ticks

def get_focal_length_plot_data(photos_stats, n_bars = 7):
    focal_length_stats = photos_stats['Focal Length']
    numeric_focal_length_stats = { float(Fraction(x.split(' ')[0])):
                                   int(focal_length_stats[x]) for x in focal_length_stats }
    
    sorted_focal_lengths = sorted(numeric_focal_length_stats.items())
    bars, ticks = aggregate_plot_data(sorted_focal_lengths, n_bars = n_bars, units = 'mm')
    
    return bars, ticks

def get_exposure_plot_data(photos_stats, n_bars = 7):
    exposure_stats = photos_stats['Exposure']
    numeric_exposure_stats = {Fraction(x): int(exposure_stats[x]) for x in exposure_stats}
    sorted_exposures = sorted(numeric_exposure_stats.items())
    
    bars,ticks = aggregate_plot_data(sorted_exposures, n_bars = n_bars, units = '')

    return bars, ticks

def get_aperture_plot_data(photos_stats, n_bars = 7):
    aperture_stats = photos_stats['Aperture']
    numeric_aperture_stats = { float(Fraction(x.split(' ')[0])):
                                   int(aperture_stats[x]) for x in aperture_stats }
    
    sorted_apertures = sorted(numeric_aperture_stats.items())
    bars, ticks = aggregate_plot_data(sorted_apertures, n_bars = n_bars, units = '')
    
    return bars, ticks
