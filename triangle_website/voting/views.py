from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from django.core.urlresolvers import reverse
import itertools
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
import requests
from django.conf import settings
import json
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
		
	user = authenticate(username=request.POST['username'], password=request.POST['password'])
	
	if not user:
		raise VotingError('Error, incorrect username/password.')
	
	# Make sure you can't vote twice.
	if not vote.set_voted(user):
		raise VotingError('Error, ' + user.username + ' has already voted in ' + vote.name)
	
	save_vote(request, vote)
	return HttpResponseRedirect(reverse('voting:results', args=[str(vote.id)]))
	
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

def results_page(request, vote_id):
	vote = get_object_or_404(Election, pk=vote_id)
	context = {'election':vote}
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
		if len(winner_set) > 1:
			winner_str += 'tie '
		if first1:
			first1 = False
		else:
			winner_str += '; '
		first2 = True
		for winner in winner_set:
			if first2:
				winner_str += winner.text
				first2 = False
			else:
				winner_str += ', ' + winner.text
	return winner_str

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
	
def sign_in(request, context={}):
	if request.method == 'POST':
		username = request.POST['user']
		password = request.POST['pwd']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			if not request.POST['remember-me']:
				request.session.set_expiry(0)
			login(request, user)
		else:
			return HttpResponseRedirect(reverse('voting:sign_in_err', args=['Incorrect username/password.']))
		return HttpResponseRedirect(reverse('voting:index'))
	else:
		print(context)
		return render(request, 'voting/login.html')
		
def sign_in_err(request, message):
	return render(request, 'voting/login.html', context={'error':message})
	
def sign_up(request):
	return render(request, 'voting/new_user.html')
	
def create_user(request):
	recap_resp = request.POST['g-recaptcha-response']
	result = requests.post('https://www.google.com/recaptcha/api/siteverify', data={'secret':settings.RECAPTCHA_SECRET, 'response':recap_resp}).text
	error = lambda message: HttpResponseRedirect(reverse('voting:sign_up_err', args=[message]))
	if json.loads(result)['success']:
		user = request.POST['user']
		passw = request.POST['pwd']
		email = request.POST['email']
		if passw != request.POST['pwd_rep']:
			return error('Passwords must match.')
		try:
			validate_email(email)
		except:
			return error('Invalid email address.')
		user = User.objects.create_user(user, password=passw, email=email)
	else:
		return error('Invalid captcha. Please try again.')
	return HttpResponseRedirect(reverse('voting:index'))
	
def sign_up_err(request, error):
	return render(request, 'voting/new_user.html', context={'error':error})
	
def signout(request):
	logout(request)
	return HttpResponseRedirect(reverse('voting:index'))
	
def home_page(request):
	return render(request, 'voting/home.html')