from django.conf.urls import url
from .views import *

app_name = 'default'
urlpatterns = [
	url(r'^calendar/$', calendar, name='calendar'),
	url(r'^$', home_page, name='index'),
]