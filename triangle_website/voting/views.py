from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def voting_index(request):
	return render(request, 'voting/index.html')