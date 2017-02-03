from django.test import TestCase
from triangle_website.voting.models import *
from triangle_website.voting.tests.helpers import UserBank
import itertools as iter
import random as rand
from django.db import reset_queries, connection
from django.conf import settings
import collections

class TestGetResults(TestCase):
    def setUp(self):
        settings.DEBUG = True
        reset_queries()
        self.users = UserBank(5)
        self.elec = Election.objects.create(name='elec', is_poll=False, creator=self.users.get(0))
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

    def test_no_first(self):
        self.vote(self.elec, {self.choice1:2, self.choice2:3})
        self.assertVoteEqual(self.ques.get_results(), [{choice} for choice in [self.choice1, self.choice2, self.choice3]])

    def test_partial_vote(self):
        self.vote(self.elec, {self.choice1:1, self.choice2:2})
        self.assertVoteEqual(self.ques.get_results(), [{choice} for choice in [self.choice1, self.choice2, self.choice3]])

    # Tests that votes are moved to runner up.
    def test_vote_realloc(self):
        self.vote(self.elec, {self.choice1:1, self.choice2:2, self.choice3:3})
        self.vote(self.elec, {self.choice1:2, self.choice2:1, self.choice3:3})
        self.vote(self.elec, {self.choice1:2, self.choice2:3, self.choice3:1})
        self.vote(self.elec, {self.choice1:1, self.choice2:2, self.choice3:3})
        self.vote(self.elec, {self.choice1:2, self.choice2:3, self.choice3:1})
        self.assertVoteEqual(self.ques.get_results(), [{self.choice1}, {self.choice2}, {self.choice3}])
        '''
        queries = collections.Counter(query['sql'] for query in connection.queries)
        for query, count in queries.items():
            print('Count: {0}, Query: {1}'.format(count, query))
        '''

    def test_large_vote(self):
        elec = Election.objects.create(name='elec', is_poll=False, creator=self.users.get(0))
        ques = Question.objects.create(name='ques', election=self.elec)
        choices = [Choice.objects.create(text='choice{0}'.format(i), question=self.ques) for i in range(7)]
        votes = list(iter.permutations(range(len(choices))))
        for i in range(100):
            selection = votes[rand.randint(0, len(votes) - 1)]
            i = 1
            voter = AnonVoter.objects.create(election=elec)
            for choice in selection:
                Vote.objects.create(voter=voter, choice=choices[choice], rank=i)
                i += 1
        ques.get_results()
