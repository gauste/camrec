import datetime

from common import *
from fetch_photo_data import *

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

def analyze_photos(photos):
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
    numeric_focal_length_stats = { float(x.split(' ')[0]):
                                   focal_length_stats[x] for x in focal_length_stats }
    
    sorted_focal_lengths = sorted(numeric_focal_length_stats.items())
    bars, ticks = aggregate_plot_data(sorted_focal_lengths, n_bars = n_bars, units = 'mm')
    
    return bars, ticks

