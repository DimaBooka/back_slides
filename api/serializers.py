from django.contrib.auth import get_user_model

from rest_framework import serializers

from slides.models import Presentation, Commentary, Event

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id',)


class PresentationSerializer(serializers.ModelSerializer):
    creator_info = SimpleUserSerializer(read_only=True, source='creator')

    def validate_creator(self, value):
        request = self.context.get('request')

        if request is None or request.user.is_staff:
            return value

        return request.user

    class Meta:
        model = Presentation
        fields = ('name', 'description', 'slides', 'thumbnail', 'creator', 'creator_info', 'date_created', 'published')
        extra_kwargs = {
            'creator': {
                'required': False,
            }
        }


class CommentarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Commentary
        fields = ('author', 'text', 'date_created', 'presentation')


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('name', 'presentation', 'date', 'state')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
