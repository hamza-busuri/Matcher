from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
from .forms import RegistrationForm, UserProfileForm, EditHobbies
from django.contrib.auth.models import User
from .models import UserProfile, Hobbies, Member
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
import datetime as D
import sys
import json
from datetime import date
from django.utils.timezone import now
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash,  authenticate,login as loginuser
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ValidationError
from django.forms import forms


# Create your views here.

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


def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        username = request.POST['username']
        first_name =request.POST['first_name']
        surname = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password1']
        if Member.objects.filter(email=email).exists():
            messages.success(request, 'Email already in use. Please try again with a different email.')
            return redirect('register')
        if form.is_valid():
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

def login(request):
    if 'username' in request.session:
        return redirect('view_profile')
    
    if request.method=='POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
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

@loggedin
def logout(request, user):
    request.session.flush()
    return redirect('home')

def viewprofilepk(request, pk):
    try: user = Member.objects.get(id=pk)
    except Member.DoesNotExist: raise Http404('Member does not exist')
    context = {
        'user': user,
        'loggedin': True
    }
    return render(request, 'matchingsite/viewprofilepk.html', context)

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

@loggedin
def view_profile(request, user):
    try: user = Member.objects.get(user=user.user)
    except Member.DoesNotExist: raise Http404('Member does not exist')
    context = {
        'user': user,
        'loggedin': True
    }
    return render(request, 'matchingsite/viewprofile.html', context)

@loggedin
def edit_profile(request, user):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user.user)
        formHob = EditHobbies(request.POST, instance=user)
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
        allowloc = request.POST.get('allow_location')
        if allowloc =='on':
            check = True
        else:
            check = False
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
            formHob.save_m2m()
            
        else:
            profile = UserProfile(profile_pic=ppic, first_name=fname, last_name=lname, email=email, gender=gender, dob=dob, location=loc)
            profile.save()
            user.user=profile
            user.save()
            hobbies = formHob.save(commit=False)
            hobbies.save()
            formHob.save_m2m()
            
        return redirect('view_profile')

    else:
        form = UserProfileForm(initial={'first_name':user.first_name, 'last_name': user.last_name, 'email':user.email,}, instance=user.user)
        formHob = EditHobbies(instance=user)
    return render(request, 'matchingsite/profile.html', {'form': form, 'formHob': formHob, 'loggedin': True, 'user':user})


@loggedin
def list_members(request, user):
    if request.method =="GET":
        # list of all other members
        #member = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies')
        member = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies')
        count = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').count()
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


@loggedin
def getgender(request,user):
    if request.method=='POST':
        search_text = request.POST['search_text']
    else:
        search_text = ''

    genders=Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').filter(user__gender__in=search_text)
    return render(request, 'matchingsite/gendermembers.html', {'genders':genders})

        

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
    
    return render(request, 'matchingsite/ageandg.html', {'ageandg':ageandg, 'messages':messages})


@loggedin
def locate(request,user):
    locations = UserProfile.objects.values('location').exclude(user=user).exclude(location__isnull=True).exclude(allow_location=False)
    json_data = json.dumps(list(locations))
    test = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').exclude(user__location__isnull=True).exclude(user__allow_location=False)[:3]
    return render(request, 'matchingsite/locate.html', {'loggedin':True, 'locations':json_data, 'data': test})
    


@loggedin
def searchuser(request, user):
    if request.method=='POST':
        search = request.POST['search']
    else:
        search=''

    users = Member.objects.exclude(user=user.user).filter(hobbies__in=user.hobbies.all()).annotate(numOfHobbies=Count('hobbies')).order_by('-numOfHobbies').filter(first_name__contains=search)
    return render(request, 'matchingsite/searchusers.html', {'users':users,})
