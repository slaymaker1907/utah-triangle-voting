from django.conf.urls import url
from .views import *

app_name = 'voting'
urlpatterns = [
	url(r'^$', voting_index, name='index'),
	url(r'^vote/(\d+)$', vote_page, name='vote')
]