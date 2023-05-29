from django.contrib import admin
from followers.models import UserFollower, UserTag


# Register your models here.
@admin.register(UserFollower)
class UserFollowerAdmin(admin.ModelAdmin):
    pass


@admin.register(UserTag)
class UserTagAdmin(admin.ModelAdmin):
    pass
