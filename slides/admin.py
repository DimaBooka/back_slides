from django.contrib import admin
from slides.models import User, Presentation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    pass
