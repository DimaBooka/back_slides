from django.contrib import admin
from slides.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass