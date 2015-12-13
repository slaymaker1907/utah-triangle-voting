from django.conf.urls import url
from .views import *

app_name = 'voting'
urlpatterns = [
	url(r'^$', voting_index, name='index'),
	url(r'^vote/(\d+)$', vote_page, name='vote'),
	url(r'^results/(\d+)$', results_page, name='results'),
	url(r'^create/$', create_vote, name='create')
]