from django.db import models

# Not currently a full model with access to DB.
class Vote:
	__id__ = 0
	def __init__(self, name="", is_poll=False):
		self.name = name
		self.id = Vote.__id__ + 1
		Vote.__id__ += 1
		self.questions = []
		self.is_poll = is_poll
		
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