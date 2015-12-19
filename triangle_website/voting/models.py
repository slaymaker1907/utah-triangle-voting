from django.db import models, transaction
from django.contrib.auth.models import User
import itertools

# Not currently a full model with access to DB.
class Election(models.Model):
	# Uncomment the following line to force creation of votes to be tied to a user.
	#creator = model.ForeignKey.(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=255)
	is_poll = models.BooleanField()
	is_open = models.BooleanField(default=True)
	
	def can_vote(self, user_ob):
		return len(Voter.objects.filter(user=user_ob).filter(election=self)) == 0
	
	# Returns either the passcode (which must be unique by db) or None if there is no passcode.
	def get_passcode(self):
		return Passcode.objects.filter(election=self).first()
		
	# Returns true if the passcode is valid or if there is no passcode.
	# This accepts a function so that getting a passcode is only invoked if
	# a passcode is actually needed.
	def check_passcode(self, get_passcode):
		code = self.get_passcode()
		return not (code != None and code.code != get_passcode())
	
	# Sets and returns the passcode.
	@transaction.atomic
	def set_passcode(self, passcode):
		result, was_created = Passcode.objects.get_or_create(election=self)
		result.code = passcode
		result.full_clean()
		result.save()
		return result
		
class Passcode(models.Model):
	code = models.CharField(max_length=255)
	election = models.ForeignKey(Election, on_delete=models.CASCADE, unique=True)
		
class Voter(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	election = models.ForeignKey(Election, on_delete=models.CASCADE)
	
	class Meta:
		unique_together = ('user', 'election')
		
class Question(models.Model):
	name = models.CharField(max_length=255)
	election = models.ForeignKey(Election, on_delete=models.CASCADE)
	
	def votes(self):
		result = []
		for voter in self.election.anonvoter_set.all():
			result.append(voter.get_vote(self))
		return result

class Choice(models.Model):
	text = models.CharField(max_length=255)
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	
	# This is a convenience method for a poll to figure out how many voted for something.
	def sum_rank(self):
		# aggregate is kind of strange and returns a dictionary instead of the value itself.
		result = Vote.objects.filter(choice=self).aggregate(models.Sum('rank'))['rank__sum']
		if result:
			return result
		else:
			return 0

# This is to collect votes for the Vote class. It stores a question mostly for convenience.
class AnonVoter(models.Model):
	election = models.ForeignKey(Election, on_delete=models.CASCADE)
	
	# This gets the rank for this user for a particular choice.
	def get_vote(self, question_arg):
		result = dict()
		# Double underscore is to make python happy and is pretty much like choice.question.
		all_votes = Vote.objects.filter(choice__question=question_arg).filter(voter=self)
		for vote in all_votes:
			result[vote.choice.id] = vote.rank
		return result

class Vote(models.Model):
	# Can get back to question through the choice field.
	choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
	rank = models.IntegerField()
	# This is anonymous and can not be traced back to a user.
	voter = models.ForeignKey(AnonVoter, on_delete=models.CASCADE)
	
class InvPasscode(Exception):
	def __init__(self, message=''):
		self.message = message