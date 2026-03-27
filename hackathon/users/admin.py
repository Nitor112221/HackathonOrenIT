from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

import users.models


class UserProfileInline(admin.TabularInline):
    model = users.models.Profile
    can_delete = False


class UserProfileAdmin(UserAdmin):
    inlines = (UserProfileInline,)

class ProfileAdmin(admin.ModelAdmin):
    pass

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
admin.site.register(users.models.Profile, ProfileAdmin)
