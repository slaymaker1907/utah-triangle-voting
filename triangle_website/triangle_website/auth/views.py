from django.shortcuts import render
from django.core.validators import validate_email
import json
import requests
from django.db import transaction
from django.core.exceptions import ValidationError
from triangle_website.common.views import get_redirect, redir_to_mess
import requests
from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from triangle_website.auth.models import *

import pdb

@login_required
def profile(request):
	brother, found = Brother.objects.get_or_create(user=request.user)
	error = None
	context = {'brother':brother}
	if request.method == 'POST':
		form = BrotherForm(request.POST, instance=brother)
		if form.is_valid():
			form.save()
	else:
		form = BrotherForm(request.GET, instance=brother)
	if form.errors:
		errors = ['{attri}: {error}'.format(error=', '.join(messages), attri=attri) for attri, messages in form.errors.items()]
		pdb.set_trace()
		context['error'] = ' '.join(errors)
	context['form'] = form
	return render(request, 'registration/profile.html', context=context)

@transaction.atomic
def register(request):
	if request.method == 'GET':
		context={'recaptcha_key':settings.RECAPTCHA_KEY}
		if 'error' in request.GET:
			context['error'] = request.GET['error']
		return render(request, 'registration/new_user.html', context=context)
	recap_resp = request.POST['g-recaptcha-response']
	result = requests.post('https://www.google.com/recaptcha/api/siteverify', data={'secret':settings.RECAPTCHA_SECRET, 'response':recap_resp}).text
	error = lambda message: get_redirect('register', error=message)
	if json.loads(result)['success']:
		username = request.POST['user']
		passw = request.POST['pwd']
		email = request.POST['email']
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		if passw != request.POST['pwd_rep']:
			return error('Passwords must match.')
		try:
			user = User.objects.create_user(username, password=passw, email=email, is_active=False, first_name=firstname, last_name=lastname)
		except:
			return error('User with username ' + username + ' already exists.')
		old_error = error
		def error(message):
			user.delete()
			return old_error(message)
		try:
			validate_password(passw, user)
		except ValidationError as e:
			return error(' '.join(e.messages))
		try:
			validate_email(email)
			if 'gmail.com' not in email:
				raise Exception('Email must be a Gmail account.')
		except:
			return error('Invalid email address. Please enter a valid Gmail email address.')
		mess = render_to_string('registration/add_user_email.txt', context={'user':user})
		try:
			mail.send_mail('Subject', mess, 'dyllongagnier@gmail.com', ['dyllongagnier@gmail.com'], fail_silently=False)
		except Exception as e:
			print(e)
			return redir_to_mess('Error in sending email', 'User ' + username + ' was created. However, failed in sending alert to webmaster. Please contact Utah Triangle leadership (including the webmaster) as soon as possible to gain full privledges on site.')
		return get_redirect('common:message', subject='Created New User', body='Created new user ' + username + '. Please be patient while the admins evaluate your account. Until then, you will only be granted limited access to the site.')
	else:
		return error('Invalid captcha. Please try again.')
