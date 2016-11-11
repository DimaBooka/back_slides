from allauth.socialaccount.models import SocialAccount, EmailAddress
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.passgen import generate_password

User = get_user_model()


@receiver(post_save, sender=SocialAccount)
def callback(instance, **kwargs):
    if not EmailAddress.objects.filter(email=instance.user.email).exists():
        gender = instance.extra_data.get('gender')
        if gender == 'male':
            instance.user.gender = 1
        elif gender == 'female':
            instance.user.gender = 2
        else:
            instance.user.gender = 3
        password = generate_password()
        instance.user.set_password(password)
        instance.user.save()
        if instance.user.email:
            send_mail(
                instance.user.email,
                'Your login {}, and your password {}'.format(instance.user.username, password),
                'sotona-streaming.com',
                [instance.user.email],
                fail_silently=False,
            )

