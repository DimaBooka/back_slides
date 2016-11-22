from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_auth.registration.app_settings import RegisterSerializer
from rest_framework import serializers
from urllib.parse import urlparse

from rest_framework.exceptions import ValidationError

from api.fields import SlidesUrlAndFileField
from slides.models import Presentation, Commentary, Event

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id',)


class PresentationSerializer(serializers.ModelSerializer):
    creator_info = SimpleUserSerializer(read_only=True, source='creator')
    creator = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    slides = SlidesUrlAndFileField()

    def validate_creator(self, value):
        request = self.context.get('request')

        if request is None or request.user.is_staff:
            return value

        return request.user

    def validate_slides(self, value):
        if type(value) is str:
            if len(value) > 255:
                raise ValidationError('Link length is very long')
            elif urlparse(value).scheme != 'https' and urlparse(value).scheme != 'http':
                raise ValidationError('Link scheme does not supported')
        return value

    def create(self, validated_data):
        instance = super().create(validated_data)
        if urlparse(instance.slides.name).scheme:
            Presentation.save_content(instance, 'create')

        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if type(validated_data.get('slides', '')) is str and urlparse(validated_data.get('slides', '')).scheme:
            Presentation.save_content(instance, 'update')
        return instance

    class Meta:
        model = Presentation
        fields = ('id', 'name', 'description', 'slides', 'thumbnail', 'creator', 'creator_info', 'date_created', 'published')
        extra_kwargs = {
            'creator': {
                'required': False,
            }
        }


class CommentarySerializer(serializers.ModelSerializer):
    author_info = SimpleUserSerializer(read_only=True, source='author')

    class Meta:
        model = Commentary
        fields = ('id', 'author', 'author_info', 'text', 'date_created', 'presentation')


class EventSerializer(serializers.ModelSerializer):
    presentation_info = PresentationSerializer(read_only=True, source='presentation')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if not isinstance(self.instance, Event) or request and request.user != self.instance.author:
            del self.fields['secret']

    def validate(self, data):
        try:
            correct_date = data.get('date_planned', '') > now()
        except:
            raise serializers.ValidationError("Incorrect or empty date")
        if not correct_date:
            raise serializers.ValidationError("Event can not be in past")
        return data

    class Meta:
        model = Event
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        new_email = validated_data.get('email', '')
        if new_email and instance.email != new_email:
            EmailAddress.objects.create(email=new_email, verified=False, primary=False, user_id=instance.id)
            EmailAddress.objects.get(email=new_email).send_confirmation()
            validated_data.pop('email')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def validate(self, attrs):
        if EmailAddress.objects.filter(email=attrs.get('email', '')).exists() and \
                      self.instance.email != attrs.get('email', ''):
            raise serializers.ValidationError('This email already exists')
        return attrs

    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']


class SlidesRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)
    birth_date = serializers.CharField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_null=True)
    timezone = serializers.CharField(required=False, allow_null=True)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'birth_date': self.validated_data.get('birth_date', ''),
            'gender': self.validated_data.get('gender', ''),
            'timezone': self.validated_data.get('timezone', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
