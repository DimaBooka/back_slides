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
    creator = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    def validate_creator(self, value):
        request = self.context.get('request')

        if request is None or request.user.is_staff:
            return value

        return request.user

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
    presentation = PresentationSerializer()

    class Meta:
        model = Event
        fields = ('id', 'name', 'presentation', 'date', 'state')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']
