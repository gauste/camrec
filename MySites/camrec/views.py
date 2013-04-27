from django.shortcuts import render

def index(request):
	categories = ['wildlife', 'nature', 'portrait', 'architecture']
	context = {'category_list': categories}
	return render(request, 'camrec/index.html', context) 

def category(request, cat):
	context = {'cat': cat}
	return render(request, 'camrec/category.html', context)
