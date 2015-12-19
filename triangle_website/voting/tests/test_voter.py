from django.test import TestCase
from voting.models import Voter, Election
from voting.tests.helpers import UserBank
from django.db.utils import IntegrityError

class VoterTest(TestCase):
	def test_mutli_user_test(self):
		elec = Election.objects.create(name='elec', is_poll=False)
		user = UserBank(1).get(0)
		Voter.objects.create(election=elec, user=user)
		with self.assertRaises(IntegrityError):
			Voter.objects.create(election=elec, user=user)