from django.db import models

# Not currently a full model with access to DB.
class Election:
	__id__ = 0
	def __init__(self, name="", is_poll=False):
		self.name = name
		self.id = Election.__id__ + 1
		Election.__id__ += 1
		self.questions = []
		self.is_poll = is_poll
		self.voted = set()
		
	def can_vote(self, user):
		return user.id not in self.voted
		
class User:
	__id__ = 0
		
class Voter:
	__id__ = 0
	def __init__(self, name=""):
		self.id = Voter.__id__
		Voter.__id__ += 1
		self.name = name
		
class Vote:
	__id__ = 0
	def __init__(self, elecId, ):
	
	
class Question:
	__id__ = 0
	def __init__(self, name=""):
		self.name = name
		self.choices = []
		self.id = Question.__id__
		Question.__id__ += 1
		
class Choice:
	__id__ = 0
	def __init__(self, text):
		self.text = text
		self.id = Choice.__id__
		Choice.__id__ += 1