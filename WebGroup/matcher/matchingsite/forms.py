from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import UserProfile, Member, Hobbies
from django.contrib.auth.forms import UserCreationForm


class DateInput(forms.DateInput):
    input_type = 'date'

class TextInput(forms.TextInput):
    input_type = 'text'

class RegistrationForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
class UserProfileForm(ModelForm):

    class Meta:
        model= UserProfile
        fields= ['profile_pic', 'first_name', 'last_name', 'email', 'gender', 'dob', 'location', 'allow_location']
        labels = {
        "profile_pic": "Profile Image",
        "first_name" : "First Name",
        "last_name" : "Surname",
        "dob" : "Date Of Birth",      
    }
        widgets = {
            'location': TextInput(attrs={'placeholder': 'Please enter accurate location for best results.'}),
        }
        help_text={
            'location': "Please provide a specific location for best results."
    }
    
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields['profile_pic'].required = False
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['dob'].widget.attrs['readonly'] = True
        


class EditHobbies(ModelForm):

    class Meta:
        model = Member
        fields=['hobbies']

    
    
