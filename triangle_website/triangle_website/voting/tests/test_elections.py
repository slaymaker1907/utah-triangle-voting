from django.test import TestCase
from triangle_website.voting.models import Election
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from triangle_website.voting.tests.helpers import UserBank

class ElectionTest(TestCase):
	def setUp(self):
		self.users = UserBank(1)
		self.elec = Election(name='elec', is_poll=False, creator=self.users.get(0))
		self.elec.save()

	# Tests that a big name will generate an error.
	def test_big_name(self):
		with self.assertRaises(ValidationError):
			elec = Election(name="Dyllon"*255, is_poll=False)

			# This is necessary because sqllite doesn't enforce VARCHAR length.
			elec.full_clean()
			elec.save()

	# Verifies that elections default to open.
	def test_open_default_true(self):
		self.assertEqual(self.elec.is_open, True)

	# Should insert a blank string
	def test_name_null(self):
		elec = Election(is_poll=True)
		with self.assertRaises(ValidationError):
			elec.full_clean()
			elec.save()

	def test_poll_null(self):
		with self.assertRaises(IntegrityError):
			elec = Election(name="")
			elec.save()

	def test_can_vote(self):
		self.assertEqual(self.elec.can_vote(self.users.get(0)), True)

	def test_correct_passcode(self):
		secret = 'pswrd'
		self.elec.set_passcode(secret)
		self.assertEqual(self.elec.check_passcode(lambda: secret), True)

	def test_incorrect_passcode(self):
		secret = 'pswrd'
		self.elec.set_passcode(secret)
		self.assertEqual(self.elec.check_passcode(lambda: 'WRONG'), False)

	# This checks that the passcode can be wrong if no passcode.
	def test_no_passcode(self):
		self.assertEqual(self.elec.check_passcode(lambda: 'WRONG'), True)

	# Tests that if no passcode, then None is ok.
	def test_none_no_passcode(self):
		self.assertEqual(self.elec.check_passcode(lambda: None), True)

	# This tests that if None is given for an elec w/ a passcode, it will return false.
	def test_none_passcode(self):
		self.elec.set_passcode('pswrd')
		self.assertEqual(self.elec.check_passcode(lambda: None), False)

	# This checks that the passcode can be set to something else.
	def test_set_passcode_twice(self):
		self.elec.set_passcode('once')
		real_code = 'twice'
		self.elec.set_passcode(real_code)
		self.assertEqual(self.elec.check_passcode(lambda: real_code), True)

	# Setting a passcode to None should fail.
	def test_set_passcode_none(self):
		with self.assertRaises(ValidationError):
			self.elec.set_passcode(None)

	# Tests that the old passcode is used if setting to a new one fails.
	def test_reset_to_bad(self):
		secret = 'good'
		with self.assertRaises(ValidationError):
			self.elec.set_passcode(secret)
			self.elec.set_passcode(None)
		self.assertEqual(self.elec.check_passcode(lambda: secret), True)
		self.assertEqual(self.elec.check_passcode(lambda: None), False)
