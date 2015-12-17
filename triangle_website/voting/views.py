from django.shortcuts import render, get_object_or_404
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
	vote = get_object_or_404(Election, pk=vote_id)
	for ques in vote.question_set.all():
		for choice in ques.choice_set.all():
			print(choice.text)
	if vote.is_poll:
		temp = 'voting/vote_poll.html'
	else:
		temp = 'voting/vote.html'
	return render(request, temp, {"vote":vote})
	
def submit_vote(request, vote_id):
	# Should never happen.
	vote = Election.objects.get(pk=vote_id)
	# TODO Make sure users can't vote twice
	if (vote.is_poll):
		for question in vote.question_set.all():
			id = str(question.id)
			if id in request.POST:
				selected = int(request.POST[str(question.id)])
				new_vote = Vote()
				new_vote.choice = Choice.objects.get(pk=selected)
				new_vote.rank = 1
				new_vote.save()
	else: # Vote is alternative vote.
		for question in vote.question_set.all():
			for choice in question.choice_set.all():
				opt = str(question.id) + ':' + str(choice.id)
				if opt in request.POST:
					# TODO Verify vote data.
					rank = int(request.POST[opt])
					new_vote = Vote()
					new_vote.choice = choice
					new_vote.rank = rank
					new_vote.save()
	return HttpResponseRedirect(reverse('voting:results', args=[str(vote.id)]))
					
def results_page(request, vote_id):
	if vote_id == "0":
		return render(request, 'voting/results.html')
	else:
		return render(request, 'voting/results_poll.html')

def new_vote(request):
	return render(request, 'voting/new_vote.html')
	
def history(request, page):
	return render(request, 'voting/history.html')

def delete_votes():
	for elec in Election.objects.all():
		elec.delete()
	
def create_vote(request):
	new_vote = Election()
	new_vote.is_poll = request.POST["voteType"] == "poll"
	new_vote.name = request.POST["voteName"]
	new_vote.save()
	try:
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
						newChoice.text = request.POST[choiceId]
						newChoice.question = newQues
						newChoice.save()
					else:
						break
			else:
				break
	except:
		new_vote.delete()
		raise
	return HttpResponseRedirect(reverse('voting:index'))