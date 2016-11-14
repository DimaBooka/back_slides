from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import build_absolute_uri
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from slugify import slugify


User = get_user_model()


class SlidesSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.id:
            if EmailAddress.objects.get(email=user.email).verified:
                perform_login(request, user, email_verification='mandatory')
            return
        try:
            user = User.objects.get(email=user.email)  # if user exists, connect the account to the existing account and login
            sociallogin.state['process'] = 'connect'
            perform_login(request, user, email_verification='mandatory')
        except User.DoesNotExist:
            username = user.first_name
            username = slugify(username) + str(user.logentry_set.creation_counter)
            user.username = username


class SlidesAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        ret = build_absolute_uri(request, url)
        return ret.replace('api/rest-auth/registration/', '')
