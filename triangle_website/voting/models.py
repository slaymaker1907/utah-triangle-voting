from django.db import models, transaction
from django.contrib.auth.models import User
import itertools
from math import ceil


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
	
	# Sets that a particular user voted in this election. Returns None on failure.
	def set_voted(self, user):
		try:
			return Voter.objects.create(user=user, election=self)
		except:
			return None
		
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
		
	# This tabulates results for an alternative vote. Be sure to do a multithreaded test on this method.
	# The result is a list of sets in order of who has won, i.e., result[0] is the absolute winner, result[1] runner up, etc.
	# A winner set will always contain at least one member. If there is more than one member, that means that all members in the
	# winner set have tied.
	@transaction.atomic
	def get_results(self, exclusion=set()):
	
		# Check to see if done.
		if len(exclusion) == len(self.choice_set.all()):
			return []
		if self.election.is_poll:
			raise Exception('Can not get results for a poll from get_results.')
				
		votes = dict()
		def add_vote(voter, dropped_choice=None):
			if dropped_choice:
				# Second arg ensures that no exception is ever thrown.
				votes.pop(dropped_choice, None)
			choice = voter.get_first_choice(self, dropped_choice)
			if choice:
				votes.get(choice, []).append(voter)

		for voter in self.get_voters():
			add_vote(voter)
		
		# Initialize winner just in case there are no voters yet.
		winner = set(self.choice_set.all())
		while len(votes) > 0:
			lowest_votes = min(map(len, votes.values()))
			
			# The last one to go will indeed be the winner.
			winner = {choice for choice, voters in votes if len(voters) == lowest_votes}
			for to_drop in winner:
				add_vote(votes[to_drop], dropped_choice=to_drop)
		
		# Exclude the winner set as well as the ones already excluded.
		return [winner] + self.get_results(exclusion | winner)
		
	def get_voters(self):
		return set(map(lambda vote: vote.voter, Vote.objects.filter(choice__question=self)))
		
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
	
	# This gets the rank for this user for a particular choice. To get the rank, call result[choice.id].
	def get_vote(self, question_arg):
		result = dict()
		# Double underscore is to make python happy and is pretty much like choice.question.
		all_votes = Vote.objects.filter(choice__question=question_arg).filter(voter=self)
		for vote in all_votes:
			result[vote.choice.id] = vote.rank
		return result
			
	# If dropped_choice=None, returns the vote with the highest rank. If dropped_choice != None, returns the next highest preference.
	def get_first_choice(self, question, dropped_choice=None):
		result = Vote.objects.filter(choice__question=question).filter(voter=self)
		if dropped_choice:
			result = result.filter(rank__gt=dropped_choice.rank)
		if len(result) == 0:
			return None
		else:
			# Sort the set and return the one with the lowest rank.
			return result.order_by('rank')[0].choice
	
class Vote(models.Model):
	# Can get back to question through the choice field.
	choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
	rank = models.IntegerField()
	# This is anonymous and can not be traced back to a user.
	voter = models.ForeignKey(AnonVoter, on_delete=models.CASCADE)

class InvPasscode(Exception):
	def __init__(self, message=''):
		self.message = message
		
class VotingError(Exception):
	def __init__(self, message=''):
		self.message = message