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
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django import template

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
		return redir_to_mess('Voting Error', str(e))
		
	
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
	
def sign_in(request, context={}):
	if request.method == 'POST':
		username = request.POST['user']
		password = request.POST['pwd']
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			if 'remember-me' not in request.POST:
				request.session.set_expiry(0)
			login(request, user)
		else:
			return HttpResponseRedirect(reverse('voting:sign_in_err', args=['Incorrect username/password.']))
		return HttpResponseRedirect(reverse('voting:index'))
	else:
		return render(request, 'voting/login.html')
		
def sign_in_err(request, message):
	return render(request, 'voting/login.html', context={'error':message})
	
def signup(request):
	return render(request, 'voting/new_user.html', context={'recaptcha_key':settings.RECAPTCHA_KEY})
	
def create_user(request):
	recap_resp = request.POST['g-recaptcha-response']
	result = requests.post('https://www.google.com/recaptcha/api/siteverify', data={'secret':settings.RECAPTCHA_SECRET, 'response':recap_resp}).text
	error = lambda message: get_redirect('voting:sign_up_err', error=message)
	if json.loads(result)['success']:
		username = request.POST['user']
		passw = request.POST['pwd']
		email = request.POST['email']
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		try:
			user = User.objects.create_user(username, password=passw, email=email, is_active=False, first_name=firstname, last_name=lastname)
		except:
			return error('User with usernam ' + username + ' already exists.')
		if passw != request.POST['pwd_rep']:
			return error('Passwords must match.')
		try:
			validate_email(email)
		except:
			return error('Invalid email address.')
		mess = get_temp_str('voting/add_user_email.txt', context={'user':user})
		try:
			send_mail('Subject', mess, 'dyllongagnier@gmail.com', ['dyllongagnier@gmail.com'], fail_silently=False)
		except Exception as e:
			print(e)
			return redir_to_mess('Error in sending email', 'User ' + username + ' was created. However, failed in sending alert to webmaster. Please contact Utah Triangle leadership (including the webmaster) as soon as possible to gain full privledges on site.')
		return get_redirect('voting:message', subject='Created New User', body='Created new user ' + username + '. Please be patient while the admins evaluate your account. Until then, you will only be granted limited access to the site.')
	else:
		return error('Invalid captcha. Please try again.')
		
def get_temp_str(temp_name, context={}):
	temp = template.loader.get_template(temp_name)
	return temp.render(context)
	
def sign_up_err(request):
	return render(request, 'voting/new_user.html', context={'error':request.GET['error'], 'recaptcha_key':settings.RECAPTCHA_KEY})

def signout(request):
	logout(request)
	return HttpResponseRedirect(reverse('voting:index'))

def home_page(request):
	return render(request, 'voting/home.html')
	
def server_message(request):
	return render(request, 'voting/server_message.html', context={'subject':request.GET['subject'], 'body':request.GET['body']})
	
def redir_to_mess(subject, body):
	return get_redirect('voting:message', subject=subject, body=body)

# Url is the url to reverse. This adds the kwargs (which should be a dict) in the form of ?param1=val1
def get_redirect(url, **kwargs):
	url = reverse(url)
	params = urlencode(kwargs)
	return HttpResponseRedirect(url + '?' + params)

@login_required
def search(request):
	vote_id = request.POST['vote_id']
	if not vote_id.isdigit():
		return get_redirect('voting:index', error='Invalid vote id ' + vote_id)
	vote = get_object_or_404(Election, pk=vote_id)
	if not vote.check_passcode(lambda:request.POST.get('passcode')):
		return get_redirect('voting:index', error='Invalid passcode for vote ' + vote_id + '.')
	return HttpResponseRedirect(reverse('voting:vote', args=[vote_id]))

# 
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