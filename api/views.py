from django.contrib.auth import get_user_model

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

from rest_framework.decorators import api_view
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.filters import PresentationFilter, EventFilter, CommentaryFilter
from api.permissions import IsOwnerOrReadOnly
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


@api_view(['GET'])
def api_root(request, format=None):

    return Response({
        'products': reverse('product-list', request=request),
        'users': reverse('user-list', request=request),
        'categories': reverse('category-list', request=request),
})


class PresentationViewSet(viewsets.ModelViewSet):
    queryset = Presentation.objects.all()
    serializer_class = PresentationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAdminUser, IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = PresentationFilter


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAdminUser, IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = EventFilter


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = CommentarySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAdminUser, IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = CommentaryFilter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
