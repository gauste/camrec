from django.shortcuts import render

def index(request):
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
	cameras = [{'camera':'Powershot G3', 'price': '$300', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg', 'http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg', 'http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Nikon D600', 'price': '$1200', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Canon Mark 5D', 'price': '$2500', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Olympus Evolt E-330', 'price': '$200', 'photos':['http://farm2.static.flickr.com/1103/567229075_2cf8456f01_m.jpg']},
			   {'camera':'Nikon D90', 'price': '$800', 'photos':''},
				]
	context = {'category':cat, 'camera_list':cameras}
	return render(request, 'camrec/category.html', context)
