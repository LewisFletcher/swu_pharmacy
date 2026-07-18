from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('practice',)
    list_filter = BaseUserAdmin.list_filter + ('practice',)


admin.site.register(User, UserAdmin)
