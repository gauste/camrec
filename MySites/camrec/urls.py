from django.conf.urls import patterns, url

from camrec import views

urlpatterns = patterns('', 
	url(r'^$', views.index),
 	url(r'^category/(?P<cat>.+)/$', views.category),
)
