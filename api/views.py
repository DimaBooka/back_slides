from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework import generics
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
    PresentationSerializer,
    UserSerializer,
)
from slides.models import (
    Commentary,
    Event,
    Presentation,
)


User = get_user_model()


class PublicPresentationsList(generics.ListCreateAPIView):
    """
    Returns list of presentations that (published == true)
    """
    queryset = Presentation.objects.filter(published=True)
    serializer_class = PresentationSerializer


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAdminUser, IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
