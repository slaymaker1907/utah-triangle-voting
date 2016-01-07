from django.test import TestCase
from voting.models import Election, Passcode
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from voting.tests.helpers import UserBank

class PasscodeTest(TestCase):
	def setUp(self):
		user = UserBank(1).get(0)
		self.elec = Election.objects.create(name='elec', is_poll=False, creator=user)

	def test_passcode_unique(self):
		with self.assertRaises(IntegrityError):
			Passcode.objects.create(election=self.elec, code='')
			Passcode.objects.create(election=self.elec, code='')
			
	def test_no_code(self):
		with self.assertRaises(ValidationError):
			passcode = Passcode(election=self.elec)
			passcode.full_clean()
			passcode.save()