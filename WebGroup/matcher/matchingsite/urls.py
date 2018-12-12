"""Matcher URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views
from django.contrib.auth.views import (
    PasswordResetView,PasswordResetDoneView, PasswordResetConfirmView,PasswordResetCompleteView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    #mainpage url
    path('', views.home, name='home'),
    #logout url
    path('logout/', views.logout, name='logout'),
    #login url
    path('login/', views.login, name='login'),
    #register url
    path('register/', views.register, name='register'),
    #change password url
    path('change-password/', views.change_password, name='change_password'),
    #edit profile url
    path('editprofile/', views.edit_profile, name = 'edit_profile'),
    #view profile url
    path('viewprofile/', views.view_profile, name='view_profile'),
    #view other members profile url
    path('viewprofilepk/<int:pk>', views.viewprofilepk, name='viewprofile'),
    path('listmembers/viewprofilepk/<int:pk>', views.viewprof, name='viewprofile'),
    #list of members url
    path('listmembers/', views.list_members, name='members'),
    #url for gender ajax feature
    path('gender/', views.getgender, name='gender'),
    #url for age range ajax feature
    path('agerange/', views.age_range, name='agerange'),
    #url for age and gender ajax feature
    path('ageandg/', views.ageAndGender, name='ageandg'),
    #url for search by first name ajax feature
    path('search/', views.searchuser, name='search'),
    #url for google maps location feature
    path('locate/', views.locate, name='locate'),
    path('uploadimage/', views.upload_image, name='uploadimage'),

    #PASSWORD RESET URLS
    path('password_reset/', PasswordResetView.as_view(template_name='registration/password_reset_form.html',success_url='done/'), name="password_reset"),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset/done/', PasswordResetCompleteView.as_view(), name="password_reset_complete"),    

    
]
