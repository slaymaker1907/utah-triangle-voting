from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from django.core.urlresolvers import reverse
import itertools
from django.db import transaction
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from triangle_website.common.views import redir_to_mess

def voting_index(request):
	get_votes = lambda current:sorted(list(Election.get_all(request.user, current=current)), key=lambda elec: -1 * elec.id)
	current_votes = get_votes(True)
	old_votes = get_votes(False)[:5]
	context = {"current_votes": current_votes, "complete_votes":old_votes, "error":request.GET.get('error')}
	return render(request, 'voting/index.html', context)

@login_required
@transaction.atomic
def vote_page(request, vote_id):
	vote = get_object_or_404(Election, pk=vote_id)
	if not vote.is_open:
		return HttpResponseRedirect(reverse('voting:results', args=[vote_id]))
	if vote.is_poll:
		temp = 'voting/vote_poll.html'
	else:
		temp = 'voting/vote.html'
	return render(request, temp, {"vote":vote})

@login_required
@transaction.atomic
def submit_vote(request, vote_id):
	try:
		# Should never fail except for very strange circumstances
		vote = Election.objects.get(pk=vote_id)

		if not vote.is_open:
			raise VotingError('Error, vote ' + vote_id + ' is not open at this time.')

		# Check passcode
		if not vote.check_passcode(lambda: request.POST['passcode']):
			raise InvPasscode()

		user = authenticate(username=request.POST['username'], password=request.POST['password'])

		if not user or not user.is_active:
			raise VotingError('Error, incorrect username/password.')

		# Make sure you can't vote twice.
		if not vote.set_voted(user):
			raise VotingError('Error, ' + user.username + ' has already voted in ' + vote.name)

		save_vote(request, vote)
		return HttpResponseRedirect(reverse('voting:results', args=[str(vote.id)]))
	except Exception as e:
		return redir_to_mess('Voting Error', e.message)


# This is just a helper method, not an actual view.
@transaction.atomic
def save_vote(request, elec):
	voter = AnonVoter(election=elec)
	voter.save()

	if (elec.is_poll):
		for question in elec.question_set.all():
			id = str(question.id)
			if id in request.POST:
				selected = int(request.POST[str(question.id)])
				new_vote = Vote(choice=Choice.objects.get(pk=selected), rank=1, voter=voter)
				new_vote.save()
	else: # Vote is alternative vote.
		for question in elec.question_set.all():
			for choice in question.choice_set.all():
				opt = str(question.id) + ':' + str(choice.id)
				if opt in request.POST:
					# TODO Verify vote data.
					new_vote = Vote(rank=int(request.POST[opt]), choice=choice, voter=voter)
					new_vote.save()

@login_required
def results_page(request, vote_id):
	vote = get_object_or_404(Election, pk=vote_id)
	can_close = vote.creator == request.user
	context = {'election':vote, 'can_close':can_close}
	if vote.is_poll:
		temp = 'voting/results_poll.html'
	else:
		temp = 'voting/results.html'
		context['winner_strs'] = {question : get_winner_str(question) for question in vote.question_set.all()}
	return render(request, temp, context)

# Constructs a string of the form one; tie second, third
def get_winner_str(question):
	winner_str = ''
	first1 = True
	voters = question.get_voters()
	for winner_set in question.get_results():
		if first1:
			first1 = False
		else:
			winner_str += '; '
		first2 = True
		for winner in winner_set:
			if first2:
				if len(winner_set) > 1:
					winner_str += 'tie '
				winner_str += winner.text
				first2 = False
			else:
				winner_str += ', ' + winner.text
	return winner_str

@login_required
def new_vote(request):
	#return get_redirect('voting:message', subject='Hello', body='World')
	return render(request, 'voting/new_vote.html')

def history(request, page):
	elections = Election.get_all(request.user)
	return render(request, 'voting/history.html', context={'elections':elections})

# A helper method for managing things. ** CAUTION: Deletes all elections **
def delete_votes():
	for elec in Election.objects.all():
		elec.delete()

@login_required
@transaction.atomic
def create_vote(request):
	new_vote = Election()
	new_vote.is_poll = request.POST["voteType"] == "poll"
	new_vote.name = request.POST["voteName"]
	new_vote.creator = request.user
	new_vote.save()
	if 'useCode' in request.POST:
		new_vote.set_passcode(request.POST['passcode'])

	# Keep iterating until a question/choice combo isn't found.
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

@login_required
def search(request):
	vote_id = request.POST['vote_id']
	if not vote_id.isdigit():
		return get_redirect('voting:index', error='Invalid vote id ' + vote_id)
	vote = get_object_or_404(Election, pk=vote_id)
	if not vote.check_passcode(lambda:request.POST.get('passcode')):
		return get_redirect('voting:index', error='Invalid passcode for vote ' + vote_id + '.')
	return HttpResponseRedirect(reverse('voting:vote', args=[vote_id]))

@login_required
@transaction.atomic
def close_vote(request, vote_id, close_vote):
	close_vote = close_vote == 'True'
	vote = get_object_or_404(Election, pk=vote_id)
	if request.user == vote.creator:
		vote.is_open= not close_vote
		vote.save()
		return redir_to_mess('Vote ' + str(vote.id) + ' Closed' if close_vote else ' Opened', 'Succesfully ' + ('closed ' if close_vote else 'opened ') + vote.name)
	else:
		return redir_to_mess('Permissions Error', 'Could not close ' + vote.name + ' because you are not the creator of that vote.')
