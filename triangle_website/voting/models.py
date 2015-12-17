from django.db import models
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