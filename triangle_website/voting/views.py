from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def voting_index(request):
	return render(request, 'voting/index.html')
	
def vote_page(request, vote_id):
	return render(request, 'voting/vote.html')