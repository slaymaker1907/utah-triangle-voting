from django.shortcuts import render
from django.http import HttpResponse
from .models import *

# Create your views here.
def voting_index(request):
	current_votes = Election.objects.filter(is_open=True)
	old_votes = Election.objects.filter(is_open=False).order_by('-id')[:5]
	context = {"current_votes": current_votes, "complete_votes":old_votes}
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