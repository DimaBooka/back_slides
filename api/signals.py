from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

User = get_user_model()


@receiver(post_save, sender=SocialAccount)
def callback(instance, **kwargs):
    if not instance.user.username:
        username = instance.extra_data.get('first_name') or instance.extra_data.get('given_name')
        username = slugify(username) + str(instance.user_id)
        instance.user.username = username
    gender = instance.extra_data.get('gender')
    if gender == 'male':
        instance.user.gender = 1
    elif gender == 'female':
        instance.user.gender = 2
    else:
        instance.user.gender = 3
    instance.user.save()
