from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, QueryDict
from analyze_photos import *

def index(request):
	if request.method == 'POST':
		architecture = request.POST.get('architecture_amount')
		art = request.POST.get('art_amount')
		car = request.POST.get('car_amount')
		cat = request.POST.get('cat_amount')
		food = request.POST.get('food_amount')
		landscape = request.POST.get('landscape_amount')
		nature = request.POST.get('nature_amount')
		people = request.POST.get('people_amount')
		pet = request.POST.get('pet_amount')
		technology = request.POST.get('technology_amount')
		wildlife = request.POST.get('wildlife_amount')
		query_string = 'architecture='+architecture+'&art='+art+'&car='+car+'&cat='+cat+'&food='+food+'&landscape='+landscape+'&nature='+nature+'&people='+people+'&pet='+pet+'&technology='+technology+'&wildlife='+wildlife
		return HttpResponseRedirect('category/' + query_string) 
	elif request.method == 'GET':
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
		context = {'category_list': categories}
		return render(request, 'camrec/index.html', context) 

def category(request, cat):
	q = QueryDict(cat)
	
	cameras = [{'camera':'Powershot G3', 'price': '$300', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg', 'http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg', 'http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Nikon D600', 'price': '$1200', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Canon Mark 5D', 'price': '$2500', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Olympus Evolt E-330', 'price': '$200', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Nikon D90', 'price': '$800', 'photos':''},
				]


        category_weights = {category: float(q[category][0]) for category in q}
        category_photo_data = load_category_photo_data()
        photos_stats = analyze_photos(category_photo_data, **category_weights)
        print photos_stats['Aperture']
        apertureData, apertureTicks = get_aperture_plot_data(photos_stats)
	#apertureData = [35, 20, 145, 51, 151, 88, 99, 185, 75, 43];
	#apertureTicks = ['0.0 - 1.8', '2.0 - 2.5', '2.6 - 3.2', '3.3 - 3.8', '3.9 - 4.3', '4.5 - 5.0', '5.1 - 5.9', '6.3 - 9.0', '9.5 - 14.0', '16.0 - 38.0'];
	context = {'category':cat, 'camera_list':cameras, 'apertureData':apertureData, 'apertureTicks':apertureTicks}
	return render(request, 'camrec/category.html', context)
