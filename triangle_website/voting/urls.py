from django.conf.urls import url
from .views import *

app_name = 'voting'
urlpatterns = [
	url(r'^$', voting_index, name='index'),
	url(r'^vote/(\d+)$', vote_page, name='vote'),
	url(r'^results/(\d+)$', results_page, name='results'),
	url(r'^new/$', new_vote, name='new'),
	url(r'^history/(\d+)$', history, name='history'),
	url(r'^create/$', create_vote, name='create'),
	url(r'^submit/(\d+)$', submit_vote, name='submit'),
	url(r'^signin/$', sign_in, name='sign_in'),
	url(r'^signin/error/(.*)$', sign_in_err, name='sign_in_err'),
	url(r'^create_user/$', create_user, name='create_user'),
	url(r'^signup/$', sign_up, name='sign_up'),
	url(r'^signup/error/(.*)/$', sign_up_err, name='sign_up_err'),
	url(r'^signout/$', signout, name='signout')
]