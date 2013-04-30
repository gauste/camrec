from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from analyze_photos import *
from interface import *

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
		top_camera_prices.append(camera_info[camera_name]['price'])
	
	cameras = [{'camera': top_cameras[i][0], 'price': '%s' % (top_camera_prices[i]), 'photos':[]} for i in range(len(top_cameras))]

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
