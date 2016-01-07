from django.db import models, transaction
from django.contrib.auth.models import User
import itertools
from math import ceil
from collections import defaultdict
from django.contrib.auth import authenticate
import pdb


# Not currently a full model with access to DB.
class Election(models.Model):
	# Uncomment the following line to force creation of votes to be tied to a user.
	creator = models.ForeignKey(User, on_delete=models.CASCADE)
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
			
	def __str__(self):
		return self.name
		
	def has_voted(self, user):
		return Voter.objects.filter(user=user).filter(election=self).exists()
		
	def can_see(self, user):
		if not (user.is_authenticated() or user.is_active):
			return False
		return self.get_passcode() is None or self.creator == user or self.has_voted(user)
		
	def get_all_voters(self):
		return Voter.objects.filter(election=self)
		
	# If current is true, then only open elections are returned.
	@staticmethod
	def get_all(user, current=False):
		if not (user.is_authenticated() or user.is_active):
			return set()
		valid_currency = lambda elec: elec.is_open or not current
		return {elec for elec in Election.objects.all() if elec.can_see(user) and valid_currency(elec)}
		
class Passcode(models.Model):
	code = models.CharField(max_length=255)
	election = models.OneToOneField(Election, on_delete=models.CASCADE, db_index=True)
	
	def __str__(self):
		return 'election:' + str(self.election) + ' code:' + str(self.code)
		
class Voter(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	election = models.ForeignKey(Election, on_delete=models.CASCADE, db_index=True)
	
	class Meta:
		unique_together = ('user', 'election')
		
	def __str__(self):
		return 'user: ' + str(self.user) + ' election:' + str(self.election)
		
class Question(models.Model):
	name = models.CharField(max_length=255)
	election = models.ForeignKey(Election, on_delete=models.CASCADE, db_index=True)
	
	def votes(self):
		result = []
		for voter in self.election.anonvoter_set.all():
			result.append(voter.get_vote(self))
		return result
		
	def __str__(self):
		return self.name
		
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
		excluded = set(exclusion)
		
		# Need to remove the excluded choices since those aren't included.
		choices = set(self.choice_set.all()) - excluded
		for choice in choices:
			votes[choice] = set()
		def remove_votes(choice):
			excluded.add(choice)
			result = votes[choice]
			votes.pop(choice, {})
			return result
		def add_vote(voter):
			choice = voter.get_first_choice(self, excluded)
			# Have to check and see if there is another voter to add in.
			if choice:
				votes[choice].add(voter)

		for voter in self.get_voters():
			add_vote(voter)
		
		# Make sure to make it a new set to avoid mutability issues.
		winner = set(choices)
		while len(votes) > 0:
			lowest_votes = min(map(len, votes.values()))
			
			# The last one to go will indeed be the winner.
			winner = {choice for choice, voters in votes.items() if len(voters) == lowest_votes}
			for to_drop in winner:
				voters = remove_votes(to_drop)
				for voter in voters:
					add_vote(voter)
		
		# Exclude the winner set as well as the ones already excluded.
		#[print(choice.text) for choice in winner]
		return [winner] + self.get_results(exclusion | winner)
		
	def get_voters(self):
		return set(map(lambda vote: vote.voter, Vote.objects.filter(choice__question=self)))
		
class Choice(models.Model):
	text = models.CharField(max_length=255)
	question = models.ForeignKey(Question, on_delete=models.CASCADE, db_index=True)
	
	# This is a convenience method for a poll to figure out how many voted for something.
	def sum_rank(self):
		# aggregate is kind of strange and returns a dictionary instead of the value itself.
		result = Vote.objects.filter(choice=self).aggregate(models.Sum('rank'))['rank__sum']
		if result:
			return result
		else:
			return 0
			
	def __str__(self):
		return self.text

# This is to collect votes for the Vote class. It stores a question mostly for convenience.
class AnonVoter(models.Model):
	election = models.ForeignKey(Election, on_delete=models.CASCADE, db_index=True)
	
	# This gets the rank for this user for a particular choice. To get the rank, call result[choice.id].
	def get_vote(self, question_arg):
		result = dict()
		# Double underscore is to make python happy and is pretty much like choice.question.
		all_votes = Vote.objects.filter(choice__question=question_arg).filter(voter=self)
		for vote in all_votes:
			result[vote.choice.id] = vote.rank
		return result
			
	# Returns the highest priority vote not in exclude. If all are excluded, then None is returned.
	@transaction.atomic
	def get_first_choice(self, question, exclude=set()):
		result = Vote.objects.filter(choice__question=question).filter(voter=self).order_by('rank')
		for vote in result:
			if vote.choice not in exclude:
				return vote.choice
		else:
			return None
			
	def __str__(self):
		return str(self.election)
	
class Vote(models.Model):
	# Can get back to question through the choice field.
	choice = models.ForeignKey(Choice, on_delete=models.CASCADE, db_index=True)
	rank = models.IntegerField()
	# This is anonymous and can not be traced back to a user.
	voter = models.ForeignKey(AnonVoter, on_delete=models.CASCADE)
	
	def __str__(self):
		return 'voter:' + str(self.voter) + ' choice:' + str(self.choice) + ' rank:' + str(self.rank)

class InvPasscode(Exception):
	def __init__(self, message='Error, invalid passcode.'):
		self.message = message
		
class VotingError(Exception):
	def __init__(self, message=''):
		self.message = message