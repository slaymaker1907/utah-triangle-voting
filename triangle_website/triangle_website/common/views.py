from django.shortcuts import render

def calendar(request):
	return render(request, 'common/calendar.html')
	
def server_message(request):
	return render(request, 'voting/server_message.html', context={'subject':request.GET['subject'], 'body':request.GET['body']})
	
def redir_to_mess(subject, body):
	return get_redirect('voting:message', subject=subject, body=body)

# Url is the url to reverse. This adds the kwargs (which should be a dict) in the form of ?param1=val1
def get_redirect(url, **kwargs):
	url = reverse(url)
	params = urlencode(kwargs)
	return HttpResponseRedirect(url + '?' + params)

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