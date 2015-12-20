from django.test import TestCase
from voting.models import Question, Election, Choice
from voting.tests.helpers import UserBank

class TestGetResults(TestCase):
	def setUp(self):
		self.users = UserBank(5)
		self.elec = Election.objects.create(name='elec', is_poll=False)
		self.ques = Question.objects.create(name='ques', election=self.elec)
		self.choice1 = Choice.objects.create(text='choice1', question=self.ques)
		self.choice2 = Choice.objects.create(text='choice2', question=self.ques)
		self.choice3 = Choice.objects.create(text='choice3', question=self.ques)
		
	# If no votes, it should be a tie among all contestants.
	def test_no_votes(self):
		result = self.ques.get_results()
		self.assertEqual(len(result), 1)
		self.assertSetEqual(result[0], {self.choice1, self.choice2, self.choice3})
		
