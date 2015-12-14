from django.shortcuts import render
from django.http import HttpResponse
from .models import *

old_votes = [Vote("Best Politicians"), Vote("World Peace"), Vote("Best LoL Player"), Vote("Religous Freedom"), Vote("Strong Encryption"), Vote("Favorite Color")]
current_votes = [Vote("President Fall 2016"), Vote("Sandwich Maker 2016"), Vote("Legislation 01/25/16")]

old_votes[0].questions = [Question("National"), Question("Local")]
old_votes[0].questions[0].choices = [Choice("Barrack Obama"), Choice("Donald Trump"), Choice("Hilary Clinton")]
old_votes[0].questions[1].choices = [Choice("John Huntsman Jr."), Choice("Jim Matheson"), Choice("Gary Herbert"), Choice("Bob Bennet")]

current_votes[0].questions = [Question("President"), Question("Political Party")]
current_votes[0].questions[0].choices = [Choice("Bernie Sanders"), Choice("Donald Trump"), Choice("Jeb Bush")]
current_votes[0].questions[1].choices = [Choice("Democrat"), Choice("Republican"), Choice("Libertarian"), Choice("Independent")]

def get_first(iter, pred):
	for ele in iter:
		if pred(ele):
			return ele
	return None

# Create your views here.
def voting_index(request):
	context = {"current_votes": current_votes, "complete_votes":old_votes[:5]}
	return render(request, 'voting/index.html', context)
	
def vote_page(request, vote_id):
	id = int(vote_id)
	vote = get_first(current_votes, lambda vt: vt.id == id)
	if vote.is_poll:
		temp = 'voting/vote_poll.html'
	else:
		temp = 'voting/vote.html'
	return render(request, temp, {"vote":vote})
				
def results_page(request, vote_id):
	if request.method == "POST":
		for param in request.POST:
			print(param + ":" + request.POST[param])
	if vote_id == "0":
		return render(request, 'voting/results.html')
	else:
		return render(request, 'voting/results_poll.html')
	
def create_vote(request):
	return render(request, 'voting/create_vote.html')
	
def history(request, page):
	return render(request, 'voting/history.html')