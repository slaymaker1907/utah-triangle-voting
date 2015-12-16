from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from django.core.urlresolvers import reverse
import itertools

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
	if vote_id == "0":
		return render(request, 'voting/results.html')
	else:
		return render(request, 'voting/results_poll.html')

def new_vote(request):
	return render(request, 'voting/new_vote.html')
	
def history(request, page):
	return render(request, 'voting/history.html')
	
def create_vote(request):
	new_vote = Election()
	if request.method == "POST":
		for param in request.POST:
			print(param + ":" + request.POST[param])
	new_vote.is_poll = request.POST["voteType"] == "poll"
	new_vote.name = request.POST["voteName"]
	new_vote.save()
	for quesCount in itertools.count(1):
		quesId = 'q' + str(quesCount)
		if quesId in request.POST:
			newQues = Question()
			newQues.name = request.POST[quesId]
			newQues.election = new_vote
			newQues.save()
			for choiceCount in itertools.count(1):
				choiceId = quesId + 'c' + str(choiceCount)
				if choiceId in request.POST:
					newChoice = Choice()
					newChoice.name = request.POST[choiceId]
					newChoice.question = newQues
					newChoice.save()
				else:
					break
		else:
			break
	return HttpResponseRedirect(reverse('voting:index'))