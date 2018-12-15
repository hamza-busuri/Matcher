from django.db import models

# Create your models here.
from django.contrib.auth.models import User

#MODEL FOR USERPROFILE
class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F' , 'Female'),
        )
    user = models.ForeignKey(
        to=User,
        null=True,
        on_delete=models.CASCADE
    )
    profile_pic = models.ImageField(upload_to='images/')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    gender = models.CharField(max_length=100, choices= GENDER_CHOICES)
    dob = models.DateField(null=True)
    location = models.CharField(max_length=100,null=True)
    allow_location = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)
    @property
    def has_member(self):
        return hasattr(self, 'member') and self.member is not None

    @property
    def member_check(self):
        return str(self.member) if self.has_member else 'NONE'

#MODEL FOR HOBBIES
class Hobbies(models.Model):
    list_Of_Hob = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.list_Of_Hob)
    
#MODEL FOR MEMBER
class Member(User):
    #One user has one user profile.
    user = models.OneToOneField(
        to=UserProfile,
        blank=True,
        null=True,
        on_delete=models.CASCADE
        )
    #many2many field between user and hobbies.
    hobbies = models.ManyToManyField(
        Hobbies,
        blank=True,
        symmetrical=False,
    )


    def __str__(self):
        return self.username
    @property
    def hobby_count(self):
        return self.hobbies.count()

    @property
    def hobbies_count(self):
        return Member.objects.filter(hobbies__id=self.id)
