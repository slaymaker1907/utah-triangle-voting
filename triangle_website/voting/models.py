from django.db import models

# Not currently a full model with access to DB.
class Vote:
	__id__ = 0
	def __init__(self, name=""):
		self.name = name
		self.id = Vote.__id__ + 1
		Vote.__id__ += 1