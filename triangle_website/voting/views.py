from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from django.core.urlresolvers import reverse
import itertools
from django.db import transaction

# Create your views here.
def voting_index(request):
	current_votes = Election.objects.filter(is_open=True)
	old_votes = Election.objects.filter(is_open=False).order_by('-id')[:5]
	context = {"current_votes": current_votes, "complete_votes":old_votes}
	return render(request, 'voting/index.html', context)
	
def vote_page(request, vote_id):
	vote = get_object_or_404(Election, pk=vote_id)
	if vote.is_poll:
		temp = 'voting/vote_poll.html'
	else:
		temp = 'voting/vote.html'
	return render(request, temp, {"vote":vote})
	
@transaction.atomic
def submit_vote(request, vote_id):
	# Should never fail except for very strange circumstances
	vote = Election.objects.get(pk=vote_id)
	
	# Check passcode
	if not vote.check_passcode(lambda: request.POST['passcode']):
		raise InvPasscode()
	
	voter = AnonVoter(election=vote)
	voter.save()
	
	# TODO Make sure users can't vote twice
	if (vote.is_poll):
		for question in vote.question_set.all():
			id = str(question.id)
			if id in request.POST:
				selected = int(request.POST[str(question.id)])
				new_vote = Vote(choice=Choice.objects.get(pk=selected), rank=1, voter=voter)
				new_vote.save()
	else: # Vote is alternative vote.
		for question in vote.question_set.all():
			for choice in question.choice_set.all():
				opt = str(question.id) + ':' + str(choice.id)
				if opt in request.POST:
					# TODO Verify vote data.
					new_vote = Vote(rank=int(request.POST[opt]), choice=choice, voter=voter)
					new_vote.save()
	return HttpResponseRedirect(reverse('voting:results', args=[str(vote.id)]))
					
def results_page(request, vote_id):
	vote = get_object_or_404(Election, pk=vote_id)
	if vote.is_poll:
		temp = 'voting/results_poll.html'
	else:
		temp = 'voting/results.html'
	return render(request, temp, {'election':vote})

def new_vote(request):
	return render(request, 'voting/new_vote.html')
	
def history(request, page):
	return render(request, 'voting/history.html')

def delete_votes():
	for elec in Election.objects.all():
		elec.delete()

@transaction.atomic
def create_vote(request):
	new_vote = Election()
	new_vote.is_poll = request.POST["voteType"] == "poll"
	new_vote.name = request.POST["voteName"]
	new_vote.save()
	if request.POST['useCode']:
		passcode = Passcode(code=request.POST['passcode'], election=new_vote)
		passcode.save()
	for quesCount in itertools.count(1):
		quesId = 'q' + str(quesCount)
		if quesId in request.POST:
			new_ques = Question(name=request.POST[quesId], election=new_vote)
			new_ques.save()
			for choiceCount in itertools.count(1):
				choiceId = quesId + 'c' + str(choiceCount)
				if choiceId in request.POST:
					newChoice = Choice(text=request.POST[choiceId], question=new_ques)
					newChoice.save()
				else:
					break
		else:
			break
	return HttpResponseRedirect(reverse('voting:index'))