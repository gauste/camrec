from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from analyze_photos import *
from interface import *
import numpy.random as random

def index(request):
	if request.method == 'POST':
                top_cameras = get_top_cameras(n=1)
                category_names = sorted(top_cameras.keys())
                category_weights = {}
                for category in category_names:
                        category_weights[category] = request.POST.get('%s_amount' % (category))

                query_string = ''
                for category in category_names:
                        query_string += '%s=%s&' % (category, category_weights[category])
                query_string = query_string[:-1]

		return HttpResponseRedirect('category/' + query_string) 

	elif request.method == 'GET':
                top_cameras = get_top_cameras(n = 3)
                top_cameras_dict = [{'category':cat, 'cameras': ', '.join([camera[0] for camera in  top_cameras[cat]])} for cat in top_cameras]
                top_cameras_dict = sorted(top_cameras_dict, key = lambda x: x['category'])
		categories = [{'category':'architecture','cameras':'Nikon D600'}, 
					  {'category':'art','cameras':'Powershot G3'},
					  {'category':'car','cameras':'Powershot G3'},
					  {'category':'cat','cameras':'Powershot G3'},
					  {'category':'food','cameras':'Powershot G3'},
					  {'category':'landscape','cameras':'Powershot G3'},
					  {'category':'nature','cameras':'Powershot G3'},
					  {'category':'people','cameras':'Powershot G3'},
					  {'category':'pet','cameras':'Powershot G3'},
					  {'category':'technology','cameras':'Powershot G3'},
					  {'category':'wildlife','cameras':'Canon Mark 5D'}
					  ]
		context = {'category_list': top_cameras_dict}
		return render(request, 'camrec/index.html', context) 

def category(request, cat):
	q = QueryDict(cat)
	f = open('cameras', 'r')
	camera_info = pickle.load(f)
	f.close()

	all_zero = True
	if len(q) != 1:
                for category in q:
                        try:
                                weight = int(q[category])
                                if weight != 0:
                                        all_zero = False
                        except:
                                continue
	else:
                all_zero = False
                category_weights = {q.keys()[0]: 1}

	if all_zero:
                return HttpResponseRedirect('/camrec/')

	if len(q) > 1:
                category_weights = {category: float(q[category]) for category in q}

	top_cameras = get_top_cameras(n=15)
	top_cameras = weighted_camera_scores(top_cameras, **category_weights)
	top_camera_prices = []
	for i in range(len(top_cameras)):
		camera_name = top_cameras[i][0]
		if 'price' in camera_info[camera_name]:
			top_camera_prices.append(camera_info[camera_name]['price'])
		else:
			top_camera_prices.append('N/A')
	
        f = open('interface_photos.dat', 'r')
        interface_photos = pickle.load(f)
        # Convert to {category: {camera: photos, ...}, ...}
        f.close()
        interface_photos = {category: {camera[0]: photos for camera, photos in interface_photos[category].iteritems()} for category in interface_photos}

        categories = filter(lambda c: category_weights[c] > 0, category_weights.keys())
        category_weight_thresholds = []
        weight_threshold = 0.0
        for category in categories:
                weight_threshold += category_weights[category]
                category_weight_thresholds.append(weight_threshold)
        max_weight_threshold = weight_threshold

        photos = defaultdict(list)
        photos_per_camera = 3
        for camera, score in top_cameras[:10]:
                photos[camera] = []
                for i in range(photos_per_camera):
                        rnd_num = random.rand() * max_weight_threshold
                        for j in range(len(category_weight_thresholds)):
                                if rnd_num < category_weight_thresholds[j]:
                                        category = categories[j]
                                        break

                        try:
                                photos_from_camera = interface_photos[category][camera]
                        except KeyError:
                                break

                        if len(photos_from_camera) == 0:
                                continue

                        photo_index = random.randint(0, len(photos_from_camera))
                        photos[camera].append(photos_from_camera[photo_index])
                        interface_photos[category][camera].remove(photos_from_camera[photo_index])


	cameras = [{'camera': top_cameras[i][0], 'price': '%s' % (top_camera_prices[i]), 'photos':photos[top_cameras[i][0]]} for i in range(len(top_cameras[:10]))]

	category_photo_data = load_category_photo_data()
	day_stats = analyze_photos(category_photo_data, time_of_day = "day", **category_weights)
	day_apertureData, day_apertureTicks = get_aperture_plot_data(day_stats)
	day_exposureData, day_exposureTicks = get_exposure_plot_data(day_stats)
	day_focalLengthData, day_focalLengthTicks = get_focal_length_plot_data(day_stats)

	night_stats = analyze_photos(category_photo_data, time_of_day = "night", **category_weights)
	night_apertureData, night_apertureTicks = get_aperture_plot_data(night_stats)
	night_exposureData, night_exposureTicks = get_exposure_plot_data(night_stats)
	night_focalLengthData, night_focalLengthTicks = get_focal_length_plot_data(night_stats)

	if len(q) > 1:
		cat = ''
		for category in q:
			if float(q[category]) > 0:
				cat = cat + category + ':' + q[category] + ' '
	
	context = {'category':cat, 'camera_list':cameras,
                   'night_apertureData':night_apertureData,
                   'night_apertureTicks':night_apertureTicks,
                   'night_focalLengthData':night_focalLengthData,
                   'night_focalLengthTicks': night_focalLengthTicks,
                   'night_exposureData': night_exposureData,
                   'night_exposureTicks': night_exposureTicks,
                   'day_apertureData':day_apertureData,
                   'day_apertureTicks':day_apertureTicks,
                   'day_focalLengthData':day_focalLengthData,
                   'day_focalLengthTicks': day_focalLengthTicks,
                   'day_exposureData': day_exposureData,
                   'day_exposureTicks': day_exposureTicks}

	return render(request, 'camrec/category.html', context)
