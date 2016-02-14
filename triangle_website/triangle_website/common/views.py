from django.shortcuts import render
from django.core.urlresolvers import reverse
from urllib.parse import urlencode
from django.http import HttpResponse, HttpResponseRedirect

def calendar(request):
	return render(request, 'common/calendar.html')

def server_message(request):
	return render(request, 'common/server_message.html', context={'subject':request.GET['subject'], 'body':request.GET['body']})

def redir_to_mess(subject, body):
	return get_redirect('common:message', subject=subject, body=body)

# Url is the url to reverse. This adds the kwargs (which should be a dict) in the form of ?param1=val1
def get_redirect(url, **kwargs):
	url = reverse(url)
	params = urlencode(kwargs)
	return HttpResponseRedirect(url + '?' + params)

def home_page(request):
	return render(request, 'common/home.html')
