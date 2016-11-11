import json

from django.core.cache import cache
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import deprecate_current_app
from django.http import HttpResponse
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter

from rest_auth.registration.views import SocialLoginView, VerifyEmailView
from rest_framework.decorators import detail_route, api_view
from rest_auth.views import PasswordResetView
from rest_framework import status

from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response

from api.filters import PresentationFilter, EventFilter, CommentaryFilter, PublishedPresentationFilter
from api.permissions import IsOwnerOrStaffOrReadOnly
from api.serializers import (
    CommentarySerializer,
    EventSerializer,
    PresentationSerializer,
)
from slides.models import (
    Commentary,
    Event,
    Presentation,
)


User = get_user_model()


class PresentationViewSet(viewsets.ModelViewSet):
    queryset = Presentation.objects.all()
    serializer_class = PresentationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrStaffOrReadOnly, )
    filter_backends = (PublishedPresentationFilter, DjangoFilterBackend, OrderingFilter)
    filter_class = PresentationFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = EventFilter

    @detail_route(methods=['post'])
    def start(self, request, pk=None):
        event = get_object_or_404(Event, id=pk)
        if event.presentation.creator == request.user:
            event.date_started = now()
            event.save(update_fields=['date_started'])
            return Response({'result': 'started'}, status=status.HTTP_200_OK)
        return Response({'error': 'You are not creator of this event.'})

    @detail_route(methods=['post'])
    def finish(self, request, pk=None):
        event = get_object_or_404(Event, id=pk)
        if event.presentation.creator == request.user:
            event.date_finished = now()
            event.save(update_fields=['date_finished'])
            return Response({'result': 'finished'}, status=status.HTTP_200_OK)
        return Response({'error': 'You are not creator of this event.'})


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = CommentarySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = CommentaryFilter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


@api_view(['POST'])
def accept_email_view(request):

    if request.method == 'POST':
        email = request.data.get('email', '')
        password = request.data.get('password', '')

        if User.objects.filter(email=email).exists() and not password:
            cache.set(request.user.id, email, 1800)
            return HttpResponse(content=json.dumps({"email": "exists"}), status=200, content_type='application/json',)

        elif password:
            if User.objects.get(email=cache.get(request.user.id)).check_password(password):
                SocialAccount.objects.filter(user_id=request.user.id).update(user_id=User.objects.get(email=cache.get(request.user.id)).pk)
                User.objects.filter(username=request.user.username).delete()
                return HttpResponse(content=json.dumps({"success": request.user.auth_token.key}),
                                    status=200,
                                    content_type='application')
            else:
                return HttpResponse(content=json.dumps({"error": "Incorrect password"}), status=400, content_type='application/json',)

        else:
            User.objects.filter(username=request.user.username).update(email=email)
            EmailAddress.objects.create(email=email, verified=True,
                                        user_id=request.user.id, primary=True)

    return HttpResponse(content=json.dumps({"success": request.user.auth_token.key}), status=201, content_type='application/json',)


class PasswordReset(PasswordResetView):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if User.objects.filter(email=serializer.validated_data['email']).count() == 0:
            return Response(
                {'error': 'User with this email does not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'success': 'Password reset e-mail has been sent.'},
            status=status.HTTP_200_OK
        )


class SlidesVerifyEmailView(VerifyEmailView):

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        return redirect('/login/')


@deprecate_current_app
def password_reset_complete(request):
    return redirect('/reset/done/')
