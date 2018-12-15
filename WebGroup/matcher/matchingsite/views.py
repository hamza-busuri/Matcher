from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .forms import RegistrationForm, UserProfileForm, EditHobbies
from django.contrib.auth.models import User
from .models import UserProfile, Hobbies, Member
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
#importing the login form and password change form from djangos auth forms.
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
import datetime as D
import sys
import json
from datetime import date
from django.utils.timezone import now
#library to use for counting hobbies.
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash,  authenticate,login as loginuser
#library for the paginator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ValidationError
from django.forms import forms
from django.db.models import Q


# Create your views here.
#This view is to check whether the logged in user is in the session and is used as a decorator to store the logged in users details.
def loggedin(view):
    def mod_view(request):
        if 'username' in request.session:
            username = request.session['username']
            try: user = Member.objects.get(username=username)
            except Member.DoesNotExist: raise Http404('Member does not exist')
            return view(request, user)
        else:
            return render(request,'matchingsite/logout.html',{})
    return mod_view

#view for home index page
def home(request):
    if 'username' in request.session:
        return redirect('view_profile')

    else:
        return render(request, 'base.html')

#view function to register the user
def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        #form which holds the data posted by the user
        form = RegistrationForm(request.POST)
        #each value is stored in a variable
        username = request.POST['username']
        first_name =request.POST['first_name']
        surname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password1']
        #this checks whether the email already exists.
        if Member.objects.filter(email=email).exists():
            messages.success(request, 'Email already in use. Please try again with a different email.')
            return redirect('register')
        if form.is_valid():
            #checks whether the user is new or if they already exists.
            user, created = Member.objects.get_or_create(username=username, email=email, first_name=first_name, last_name=surname, password = password)
            if created:
                user.set_password(password)
                user.save()
                profile = UserProfile()
                profile.user=user
                profile.save()
                user.user=profile
                user.save()
            messages.success(request,'Account has been created successfully.')
            return redirect('login')
        
        else:
            messages.success(request, 'Please make sure you are entering the correct values')
           
    else:
        form = RegistrationForm()
    return render(request, 'matchingsite/register.html', {'form': form})

#view function to allow the user to login.
def login(request):
    #checks to see whether the user is already logged in. If yes, redirect them to their profile
    if 'username' in request.session:
        return redirect('view_profile')
    
    if request.method=='POST':
        #stores the request,post information in the form.
        form = AuthenticationForm(request.POST)
        #gets the user name and password for the login page
        username = request.POST['username']
        password = request.POST['password']
        #authenticate() method to verify the credentials
        user = authenticate(username=username, password=password)
        if user is not None:
            user = Member.objects.get(username=username)
            # remember user in session variable
            request.session['username'] = username
            request.session['password'] = password
            context = {
               'user': user,
               'loggedin': True,
            }
            response = render(request, 'matchingsite/viewprofile.html', context)
            # remember last login in cookie
            now = D.datetime.utcnow()
            max_age = 365 * 24 * 60 * 60  #one year
            delta = now + D.timedelta(seconds=max_age)
            format = "%a, %d-%b-%Y %H:%M:%S GMT"
            expires = D.datetime.strftime(delta, format)
            response.set_cookie('last_login',now,expires=expires)
            return response
        else:
            messages.error(request,'Username or password is incorrect.')
            return redirect('login')
             
    else:
        form = AuthenticationForm()
        return render(request,'matchingsite/login.html', {'form':form,})

@loggedin
def change_password(request, user):
    #This view was used from djangos change password forms and uses update_session_auth_hash to update the password.
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password has been changed")
            return redirect('view_profile')
        else:
            messages.error(request, "Old password maybe incorrect or two passwords do not match. Please try again.")
            form = PasswordChangeForm(user=user)
            context = {'form': form, 'loggedin':True, 'user':user}
            return render(request, 'matchingsite/change_password.html', context)
            
    else:
        form = PasswordChangeForm(user=user)
        context = {'form': form, 'loggedin':True, 'user':user}
        return render(request, 'matchingsite/change_password.html', context)

#view function to logout. Redirects to base page.
@loggedin
def logout(request, user):
    request.session.flush()
    return redirect('home')

#view function which allows the user to display another users profile
def viewprofilepk(request, pk):
    try: user = Member.objects.get(id=pk)
    except Member.DoesNotExist: raise Http404('Member does not exist')
    context = {
        'user': user,
        'loggedin': True
    }
    return render(request, 'matchingsite/viewprofilepk.html', context)

#this view is used for the ajax function for displaying a quick view of the users profile in the table.
def viewprof(request, pk):
    try: user = Member.objects.get(id=pk)
    except Member.DoesNotExist: raise Http404('Member does not exist')
    data = {
            'user':str(user),
            'pic':json.dumps(str(user.user.profile_pic)),
            'email':user.email,
            'gender':user.user.gender,
            'dob':user.user.dob,
            }
    return JsonResponse(data)

#view function for the user to display their own profile.
@loggedin
def view_profile(request, user):
    try: user = Member.objects.get(user=user.user)
    except Member.DoesNotExist: raise Http404('Member does not exist')
    context = {
        'user': user,
        'loggedin': True
    }
    return render(request, 'matchingsite/viewprofile.html', context)

#view function to allow the user to edit their profile.
@loggedin
def edit_profile(request, user):
    if request.method == 'POST':
        #as it is two different forms, retrieve the values from both.
        form = UserProfileForm(request.POST, request.FILES, instance=user.user)
        formHob = EditHobbies(request.POST, instance=user)
        #checks to see if user has a picture.
        if 'profile_pic' in request.FILES:
            ppic = request.FILES['profile_pic']
        fname = request.POST['first_name']
        lname = request.POST['last_name']
        email = request.POST['email']
        gender = request.POST['gender']
        dob = request.POST['dob']
        loc = request.POST['location']
        if 'hobbies' in request.POST:
            hobs = request.POST['hobbies']
        #django displays output for checkbox as on so condition was used to set it to true or false as Djangos db allows only True/False.
        allowloc = request.POST.get('allow_location')
        if allowloc =='on':
            check = True
        else:
            check = False

        #This is a condition to check if the user already has a profile then update the existing information.
        if user.user:
            if 'profile_pic' in request.FILES:
                user.user.profile_pic =ppic
            user.user.first_name = fname
            user.user.last_name =lname
            user.user.email = email
            user.user.gender = gender
            user.user.dob = dob
            user.user.allow_location = check
            user.user.location = loc
            user.user.save()
            user.save()
            hobbies = formHob.save(commit=False)
            hobbies.save()
            #save the hobbies using m2m() as it is many2many field
            formHob.save_m2m()

        #if the user does not have values in their profile then store the new values.
        else:
            profile = UserProfile(profile_pic=ppic, first_name=fname, last_name=lname, email=email, gender=gender, dob=dob, location=loc)
            profile.save()
            user.user=profile
            user.save()
            hobbies = formHob.save(commit=False)
            hobbies.save()
            #save the hobbies using m2m() as it is many2many field
            formHob.save_m2m()
            
        return redirect('view_profile')

    else:
        form = UserProfileForm(initial={'first_name':user.first_name, 'last_name': user.last_name, 'email':user.email,}, instance=user.user)
        formHob = EditHobbies(instance=user)
    return render(request, 'matchingsite/profile.html', {'form': form, 'formHob': formHob, 'loggedin': True, 'user':user})


@loggedin
def list_members(request, user):
    if request.method =="GET":
        #This query uses QuerySet annotation/aggregation to check if hobbies match. I felt this is more convenient than using for loops.
        member = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies')
        #query to get how many users the logged in user matched with
        count = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').count()
        #functionality to use paginator depending on how many values in queryset. It will display 5 in each page.                                                                                                                                                                                     
        page = request.GET.get('page')
        paginator = Paginator(member, 5)

        try:
            members = paginator.page(page)
        except PageNotAnInteger:
            members = paginator.page(1)
        except EmptyPage:
            members = paginator.page(paginator.num_pages)
        context = {
            'username': user.username,
            'members': members,
            'loggedin': True,
            'count':count,
        }
        return render(request, 'matchingsite/listmembers.html', context)

#view for the ajax function to filter for gender
@loggedin
def getgender(request,user):
    if request.method=='POST':
        search_text = request.POST['search_text']
    else:
        search_text = ''

    genders=Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').filter(user__gender__in=search_text)
    return render(request, 'matchingsite/gendermembers.html', {'genders':genders,})

#view for the ajax function to filter for age
@loggedin
def age_range(request, user):
    current = now().date()
    if request.method=='POST':
        age = request.POST['age']
        if age=='0':
            min_date = date(current.year - 0, current.month, current.day)
            max_date = date(current.year - 30, current.month, current.day)
        if age=='1':
            min_date = date(current.year - 30, current.month, current.day)
            max_date = date(current.year - 50, current.month, current.day)

        if age=='2':
            min_date = date(current.year - 50, current.month, current.day)
            max_date = date(current.year - 150, current.month, current.day)

        if age=='Age':
            min_date = date(current.year - 0, current.month, current.day)
            max_date = date(current.year - 0, current.month, current.day)
            
            
    else:
        print('Not working')


    ages = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').filter(user__dob__gte=max_date,
                                    user__dob__lte=min_date)
    return render(request, 'matchingsite/agemembers.html', {'ages':ages}) 

#view for the ajax function to filter for age and gender
@loggedin
def ageAndGender(request, user):
    current = now().date()
    if request.method=='POST':
        age = request.POST['age']
        search_text = request.POST['search_text']
        
        if age=='0' and search_text=='M' or search_text=='':
            min_date = date(current.year - 0, current.month, current.day)
            max_date = date(current.year - 30, current.month, current.day)
            search_text='M'
        if age=='1' and search_text=='M' or search_text=='' :
            min_date = date(current.year - 30, current.month, current.day)
            max_date = date(current.year - 50, current.month, current.day)
            search_text='M'
        if age=='2' and search_text=='M'or search_text=='':
            min_date = date(current.year - 50, current.month, current.day)
            max_date = date(current.year - 150, current.month, current.day)
            search_text='M'

        if age=='0' and search_text=='F' or search_text=='':
            min_date = date(current.year - 0, current.month, current.day)
            max_date = date(current.year - 30, current.month, current.day)
            search_text='F'
        if age=='1' and search_text=='F' or search_text=='':
            min_date = date(current.year - 30, current.month, current.day)
            max_date = date(current.year - 50, current.month, current.day)
            search_text='F'

        if age=='2' and search_text=='F' or search_text=='':
            min_date = date(current.year - 50, current.month, current.day)
            max_date = date(current.year - 150, current.month, current.day)
            search_text='F'

        if age=='Age' and search_text=='Gender':
            min_date = date(current.year - 0, current.month, current.day)
            max_date = date(current.year - 0, current.month, current.day)
            search_text=''
            
        if age=='Age' and search_text!='':
            min_date = date(current.year - 0, current.month, current.day)
            max_date = date(current.year - 0, current.month, current.day)
            search_text=''

        if age!='' and search_text=='Gender':
            min_date = date(current.year - 0, current.month, current.day)
            max_date = date(current.year - 0, current.month, current.day)
            search_text=''
                   
    else:
        print('Not working')


    ageandg = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').filter(user__dob__gte=max_date,
                                    user__dob__lte=min_date).filter(user__gender__in=search_text)
    
    return render(request, 'matchingsite/ageandg.html', {'ageandg':ageandg, 'messages':messages,})

#view function for the google maps extra feature. It checks whether the user has a location and if they allow their location on.
@loggedin
def locate(request,user):
    locate = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').exclude(user__location__isnull=True).exclude(user__allow_location=False).values('user__location')
    json_data = json.dumps(list(locate))
    top3 = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').exclude(user__location__isnull=True).exclude(user__allow_location=False)[:3]
    every = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').exclude(user__location__isnull=True).exclude(user__allow_location=False)
    return render(request, 'matchingsite/locate.html', {'loggedin':True, 'locations':json_data, 'data': top3, 'data1':every})
    

#view function to allow the user to search by first name
@loggedin
def searchuser(request, user):
    if request.method=='POST':
        search = request.POST['search']
    else:
        search=''

    users = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').filter(first_name__contains=search)
    return render(request, 'matchingsite/searchusers.html', {'users':users,})

#view function to upload the image of a profile user asynchronously.
@loggedin
def upload_image(request, user):
    if 'img_file' in request.FILES:
        image_file = request.FILES['img_file']
        if user.user:
            # if user doesn't have a profile yet
            # need to create a profile first
            user.user.profile_pic = image_file
            user.user.save()
        return HttpResponse(user.user.profile_pic.url)
    else:
        raise Http404('Image file not received')
