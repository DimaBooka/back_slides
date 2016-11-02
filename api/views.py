from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.views.generic import TemplateView
from rest_auth.registration.views import SocialLoginView, VerifyEmailView
from rest_framework.decorators import detail_route
from rest_auth.views import PasswordResetView
from rest_framework import status

from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

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


class RegisterConfirmationView(TemplateView):
    template_name = 'registration-confirm-page.html'

    def get_context_data(self, **kwargs):
        kwargs['key'] = self.kwargs['key']
        return super().get_context_data(**kwargs)


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
        return redirect('/#!/login/')
