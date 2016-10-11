from django.contrib.auth import get_user_model

from rest_framework import serializers

from slides.models import Presentation, Commentary, Event

User = get_user_model()


class PresentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Presentation
        fields = ('name', 'description', 'slides', 'thumbnail', 'creator', 'date_created', 'published')


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
