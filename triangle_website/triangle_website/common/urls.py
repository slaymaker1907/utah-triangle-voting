from django.conf.urls import url
from triangle_website.common.views import *

app_name = 'common'
urlpatterns = [
	url(r'^calendar/$', calendar, name='calendar'),
	url(r'^$', home_page, name='index'),
	url(r'^message/$', server_message, name='message'),
	url(r'^signup/$', signup, name='signup'),
	url(r'^create_user/$', create_user, name='create_user'),
	url(r'^sign_up_err/$', sign_up_err, name='sign_up_err'),
]