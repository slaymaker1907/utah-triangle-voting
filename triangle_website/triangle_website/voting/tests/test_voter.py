from django.test import TestCase
from voting.models import *
from voting.tests.helpers import UserBank
from django.db.utils import IntegrityError

class VoterTest(TestCase):
	def setUp(self):
		self.users = UserBank(5)
		self.elec = Election.objects.create(name='elec', is_poll=False, creator=self.users.get(0))
		self.ques = Question.objects.create(name='ques', election=self.elec)
		self.choice1 = Choice.objects.create(text='choice1', question=self.ques)
		self.choice2 = Choice.objects.create(text='choice2', question=self.ques)
		self.choice3 = Choice.objects.create(text='choice3', question=self.ques)
		
	def vote(self, elec, ranking):
		voter = AnonVoter.objects.create(election=elec)
		for choice, rank in ranking.items():
			Vote.objects.create(voter=voter, choice=choice, rank=rank)
		return voter

	def test_mutli_user_test(self):
		user = self.users.get(0)
		elec = Election.objects.create(name='elec', is_poll=False, creator=user)
		Voter.objects.create(election=elec, user=user)
		with self.assertRaises(IntegrityError):
			Voter.objects.create(election=elec, user=user)
			
	# Tests that if a partial vote, returns None if all choices are excluded that the user selected.
	def test_partial_highest_rank(self):
		voter = self.vote(self.elec, {self.choice1:1, self.choice2:2})
		self.assertEqual(self.choice1, voter.get_first_choice(self.ques))
		self.assertEqual(self.choice2, voter.get_first_choice(self.ques, exclude={self.choice1}))
		self.assertIsNone(voter.get_first_choice(self.ques, exclude={self.choice1, self.choice2}))