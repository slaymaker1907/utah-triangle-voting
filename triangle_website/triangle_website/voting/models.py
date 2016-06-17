from django.db import models, transaction
from django.contrib.auth.models import User
from collections import defaultdict
from django.contrib.auth import authenticate
import uuid
import collections


# Not currently a full model with access to DB.
class Election(models.Model):
    # Uncomment the following line to force creation of votes to be tied to a user.
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_poll = models.BooleanField()
    is_open = models.BooleanField(default=True)

    def can_vote(self, user_ob):
        return len(Voter.objects.filter(user=user_ob).filter(election=self)) == 0

    # Returns either the passcode (which must be unique by db) or None if there is no passcode.
    def get_passcode(self):
        return Passcode.objects.filter(election=self).first()

    # Returns true if the passcode is valid or if there is no passcode.
    # This accepts a function so that getting a passcode is only invoked if
    # a passcode is actually needed.
    def check_passcode(self, get_passcode):
        code = self.get_passcode()
        return not (code != None and code.code != get_passcode())

    # Sets and returns the passcode.
    @transaction.atomic
    def set_passcode(self, passcode):
        result, was_created = Passcode.objects.get_or_create(election=self)
        result.code = passcode
        result.full_clean()
        result.save()
        return result

    # Sets that a particular user voted in this election. Returns None on failure.
    def set_voted(self, user):
        try:
            return Voter.objects.create(user=user, election=self)
        except:
            return None

    def __str__(self):
        return self.name

    def has_voted(self, user):
        return Voter.objects.filter(user=user).filter(election=self).exists()

    def can_see(self, user):
        if not (user.is_authenticated() or user.is_active):
            return False
        return self.get_passcode() is None or self.creator == user or self.has_voted(user)

    def get_all_voters(self):
        return Voter.objects.filter(election=self).order_by('user__first_name', 'user__last_name')

    # If current is true, then only open elections are returned.
    @staticmethod
    def get_all(user, current=False):
        if not (user.is_authenticated() or user.is_active):
            return set()
        valid_currency = lambda elec: elec.is_open or not current
        return {elec for elec in Election.objects.all() if elec.can_see(user) and valid_currency(elec)}

class Passcode(models.Model):
    code = models.CharField(max_length=255)
    election = models.OneToOneField(Election, on_delete=models.CASCADE, db_index=True)
    def __str__(self):
        return 'election:' + str(self.election) + ' code:' + str(self.code)

class Voter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = ('user', 'election')

    def __str__(self):
        return 'user: ' + str(self.user) + ' election:' + str(self.election)

def get_vote_tabulator(question):
        # Get all vote choices -- necessary just in case no votes for candidate.
        choices = set(question.choice_set.all())
        # Get all votes.
        votes_database = Vote.objects.all().filter(choice__question=question)
        votes = collections.defaultdict(set)
        for vote in votes_database:
            votes[vote.voter].add(vote)
        return VoteTabulator(choices, votes)

class VoteTabulator:
    def __init__(self, choices, votes):
        self.choices = choices
        self.votes = votes

    def exclude(self, excluded):
        for exclude in excluded:
            self.choices.discard(exclude)
            for voter, voter_votes in list(self.votes.items()):
                self.votes[voter] = {vote for vote in voter_votes if vote.choice not in excluded}

    def clone(self):
        choices = set(self.choices)
        votes = collections.defaultdict(set, ((voter, set(votes)) for voter, votes in self.votes.items()))
        return VoteTabulator(choices, votes)

    def compute_winner_count(self):
        vote_rank = lambda vote: vote.rank
        return collections.Counter(min(votes, key=vote_rank).choice for voter, votes in self.votes.items() if len(votes) > 0)

    def get_losers(self):
        vote_res = self.compute_winner_count()
        min_votes = min((vote_res[choice] for choice in self.choices), default=0)
        return [choice for choice in self.choices if vote_res[choice] == min_votes]

    def compute_winner(self):
        first_clone = self.clone()
        result = list()
        while len(first_clone.choices) > 0:
            second_clone = first_clone.clone()
            while len(second_clone.choices) > 0:
                losers = second_clone.get_losers()
                second_clone.exclude(losers)
            result.append(set(losers))
            first_clone.exclude(losers)
        return result

class Question(models.Model):
    name = models.CharField(max_length=255)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, db_index=True)

    def votes(self):
        result = []
        for voter in self.election.anonvoter_set.all():
            result.append(voter.get_vote(self))
        return result

    def __str__(self):
        return self.name

    # This tabulates results for an alternative vote. Be sure to do a multithreaded test on this method.
    # The result is a list of sets in order of who has won, i.e., result[0] is the absolute winner, result[1] runner up, etc.
    # A winner set will always contain at least one member. If there is more than one member, that means that all members in the
    # winner set have tied.
    @transaction.atomic
    def get_results(self, exclusion=set()):
        # Check to see if done.
        if len(exclusion) == len(self.choice_set.all()):
            return []
        if self.election.is_poll:
            raise Exception('Can not get results for a poll from get_results.')

        result = get_vote_tabulator(self)
        result.exclude(exclusion)
        return result.compute_winner()

    def get_voters(self):
        return set(map(lambda vote: vote.voter, Vote.objects.filter(choice__question=self)))

class Choice(models.Model):
    text = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_index=True)

    # This is a convenience method for a poll to figure out how many voted for something.
    def sum_rank(self):
        # aggregate is kind of strange and returns a dictionary instead of the value itself.
        result = Vote.objects.filter(choice=self).aggregate(models.Sum('rank'))['rank__sum']
        if result:
            return result
        else:
            return 0

    def __str__(self):
        return self.text

# This is to collect votes for the Vote class. It stores a question mostly for convenience.
class AnonVoter(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, db_index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.responses = dict()

    # This gets the rank for this user for a particular choice. To get the rank, call result[choice.id].
    def get_vote(self, question_arg):
        result = dict()
        # Double underscore is to make python happy and is pretty much like choice.question.
        all_votes = Vote.objects.filter(choice__question=question_arg).filter(voter=self)
        for vote in all_votes:
            result[vote.choice.id] = vote.rank
        return result

    # Returns the highest priority vote not in exclude. If all are excluded, then None is returned.
    @transaction.atomic
    def get_first_choice(self, question, exclude=set()):
        result = Vote.objects.filter(choice__question=question).filter(voter=self).order_by('rank')
        for vote in result:
            if vote.choice not in exclude:
                return vote.choice
        else:
            return None

    def __str__(self):
        return str(self.election)

class Vote(models.Model):
    # Can get back to question through the choice field.
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, db_index=True)
    rank = models.IntegerField()
    # This is anonymous and can not be traced back to a user.
    voter = models.ForeignKey(AnonVoter, on_delete=models.CASCADE)

    def __str__(self):
        return 'voter:' + str(self.voter) + ' choice:' + str(self.choice) + ' rank:' + str(self.rank)

class InvPasscode(Exception):
    def __init__(self, message='Error, invalid passcode.'):
        self.message = message

class VotingError(Exception):
    def __init__(self, message=''):
        self.message = message
