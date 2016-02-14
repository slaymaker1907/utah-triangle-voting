from django.conf.urls import url
from triangle_website.voting.views import *

app_name = 'common'
urlpatterns = [
	url(r'^calendar/$', calendar, name='calendar'),
	url(r'^$', home_page, name='index'),
]