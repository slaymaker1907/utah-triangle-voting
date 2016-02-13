from django.contrib.auth.models import User

# A helper class for quickly generating and using users.
class UserBank:
	def __init__(self, count):
		self.__users__ = []
		for i in range(count):
			username = str(i)
			self.__users__.append(User.objects.create_user(username=username))
			
	def get(self, id):
		return self.__users__[id]