from django.contrib import admin
from slides.models import User, Presentation, Commentary, Event


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    pass


@admin.register(Commentary)
class CommentaryAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class CommentaryAdmin(admin.ModelAdmin):
    pass
