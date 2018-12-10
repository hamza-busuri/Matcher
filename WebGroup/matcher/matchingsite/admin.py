from django.contrib import admin

from django.db import models
from .models import UserProfile, Hobbies, Member
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Hobbies)
admin.site.register(Member)
