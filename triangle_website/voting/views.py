from django.shortcuts import render
from django.http import HttpResponse
from .models import *

old_votes = [Vote("Best Santa Clause"), Vote("World Peace"), Vote("Best LoL Player"), Vote("Religous Freedom"), Vote("Strong Encryption"), Vote("Favorite Color")]
current_votes = [Vote("President Fall 2016"), Vote("Sandwich Maker 2016"), Vote("Legislation 01/25/16")]

# Create your views here.
def voting_index(request):
	context = {"current_votes": current_votes, "complete_votes":old_votes[:5]}
	return render(request, 'voting/index.html', context)
	
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
	
def history(request, page):
	return render(request, 'voting/history.html')