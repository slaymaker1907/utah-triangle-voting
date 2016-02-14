from django.db.models import *
from django.contrib.auth.models import User
from django import forms

class AcademicYear:
    unknown = 0
    freshman = 1
    sophomore = 2
    junior = 3
    senior = 4
    alumnus = 5
    ALL = (
        (unknown, 'Unknown'),
        (freshman, 'Freshman'),
        (sophomore, 'Sophomore'),
        (junior, 'Junior'),
        (alumnus, 'Alumnus'),
    )

class MemberStatus:
    unknown = 0
    pledge = 1
    active = 2
    ALL = (
        (unknown, 'Unknown'),
        (pledge, 'Pledge'),
        (active, 'Active'),
    )

class TShirtSize:
    unknown = 0
    small = 1
    medium = 2
    large = 3
    xlarge = 4
    xxlarge = 5
    xxxlarge = 6
    ALL = (
        (unknown, 'Unknown'),
        (small, 'S'),
        (medium, 'M'),
        (large, 'L'),
        (xlarge, 'XL'),
        (xxlarge, 'XXL'),
        (xxxlarge, 'XXXL'),
    )

class Brother(Model):
    user = OneToOneField(User, on_delete=CASCADE, db_index=True)
    year = IntegerField(default=AcademicYear.unknown, choices=AcademicYear.ALL)
    major = CharField(max_length=100, default='')
    address = TextField(default='')
    parents_address = TextField('')
    emergency_contact = TextField(default='')

    position = CharField(max_length=100, default='')
    member_status = IntegerField(default=MemberStatus.unknown, choices=MemberStatus.ALL)
    initiation_date = DateField(null=True)

    tshirt = IntegerField(default=TShirtSize.unknown, choices=TShirtSize.ALL)
    student_orgs = TextField(default='')
    allergies = TextField(default='')
    interests = TextField(default='')

class BrotherForm(forms.ModelForm):
    class Meta:
        model=Brother
        fields = ['year', 'major', 'address', 'parents_address', 'emergency_contact', 'position', 'member_status',
         'initiation_date', 'tshirt', 'student_orgs', 'allergies', 'interests']
