from django.conf.urls import url
from triangle_website.common.views import *
from django.db import transaction

app_name = 'common'
urlpatterns = [
	url(r'^calendar/$', calendar, name='calendar'),
	url(r'^$', home_page, name='index'),
	url(r'^message/$', server_message, name='message'),
]
