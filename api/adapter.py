from allauth.account.adapter import DefaultAccountAdapter
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

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_username, user_email, user_field

        data = form.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        username = data.get('username')
        birth_date = data.get('birth_date')
        gender = data.get('gender')
        timezone = data.get('timezone')
        user_email(user, email)
        user_username(user, username)
        user.all_fields_completed = True
        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)
        if birth_date:
            user_field(user, 'birth_date', birth_date)
        if gender:
            user_field(user, 'gender', gender)
        if timezone:
            user_field(user, 'timezone', timezone)
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user
