from django.contrib import admin
from .models import siteUser

@admin.register(siteUser)
class AuthAdmin(admin.ModelAdmin):
    list_display = ('id','username','jifen','date_joined')