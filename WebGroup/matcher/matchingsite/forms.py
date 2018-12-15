from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import UserProfile, Member, Hobbies
from django.contrib.auth.forms import UserCreationForm

#Added a TextInput class to add a placeholder to the location field
class TextInput(forms.TextInput):
    input_type = 'text'

#Registration form class to display fields from Djangos User model.
class RegistrationForm(UserCreationForm):
    class Meta:
        model = Member
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

#Method which allows to override the 'required' attribute of the field.
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

#UserProfile form class to display fields fromUserprofile Model.      
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
        #widget which inputs a placeholder in location field.
        widgets = {
            'location': TextInput(attrs={'placeholder': 'Please enter accurate location for best results.'}),
        }

    #Method which allows to override the 'required' attribute of the field.
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields['profile_pic'].required = False
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['dob'].widget.attrs['readonly'] = True
        

#Edit hobbies form class to display fields from Custom Member model. 
class EditHobbies(ModelForm):

    class Meta:
        model = Member
        fields=['hobbies']

    
    
