from django.test import TestCase
from voting.models import *
from voting.tests.helpers import UserBank

class TestGetResults(TestCase):
	def setUp(self):
		self.users = UserBank(5)
		self.elec = Election.objects.create(name='elec', is_poll=False)
		self.ques = Question.objects.create(name='ques', election=self.elec)
		self.choice1 = Choice.objects.create(text='choice1', question=self.ques)
		self.choice2 = Choice.objects.create(text='choice2', question=self.ques)
		self.choice3 = Choice.objects.create(text='choice3', question=self.ques)
		
	def assertVoteEqual(self, actual, expected):
		self.assertEqual(len(actual), len(expected))
		for actWin, expWin in zip(actual, expected):
			self.assertSetEqual(actWin, expWin)
		
	# If no votes, it should be a tie among all contestants.
	def test_no_votes(self):
		result = self.ques.get_results()
		self.assertVoteEqual(result, [{self.choice1, self.choice2, self.choice3}])
		
	def vote(self, elec, ranking):
		voter = AnonVoter.objects.create(election=elec)
		for choice, rank in ranking.items():
			Vote.objects.create(voter=voter, choice=choice, rank=rank)
		
	def test_basic_vote(self):
		self.vote(self.elec, {self.choice1:1, self.choice2:2, self.choice3:3})
		self.assertVoteEqual(self.ques.get_results(), [{choice} for choice in [self.choice1, self.choice2, self.choice3]])