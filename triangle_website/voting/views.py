from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def voting_index(request):
	return render(request, 'voting/index.html')
	
def vote_page(request, vote_id):
	if vote_id == "1234":
		return render(request, 'voting/vote.html')
	else:
		return render(request, 'voting/vote_poll.html')
	
def results_page(request, vote_id):
	if vote_id == "0":
		return render(request, 'voting/results.html')
	else:
		return render(request, 'voting/results_poll.html')
	
def create_vote(request):
	return render(request, 'voting/create_vote.html')