from django.db.models import *
from django.contrib.auth.models import User

class AcademicYear:
    unknown = 0
    freshman = 1
    sophomore = 2
    junior = 3
    senior = 4
    alumnus = 5

class MemberStatus:
    unknown = 0
    pledge = 1
    active = 2

class TShirtSize:
    unknown = 0
    small = 1
    medium = 2
    large = 3
    xlarge = 4
    xxlarge = 5

class Brother(Model):
    position = CharField(max_length=100, default='')
    year = IntegerField(default=AcademicYear.unknown)
    major = CharField(max_length=100, default='')
    member_status = IntegerField(MemberStatus.unknown)
    address = TextField(default='')
    initiation_date = DateField(null=True)
    emergency_contact = TextField(default='')
    tshirt = TShirtSize.unknown
    student_orgs = TextField(default='')
    allergies = TextField(default='')
    interests = TextField(default='')
    parents_address = TextField('')
    user = OneToOneField(User, on_delete=CASCADE, db_index=True)
