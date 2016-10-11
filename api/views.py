from rest_framework import generics
from slides.models import Presentation
from .serializers import PresentationSerializer


class PublicPresentationsList(generics.ListCreateAPIView):
    """
    Returns list of presentations that (published == true)
    """
    queryset = Presentation.objects.filter(published=True)
    serializer_class = PresentationSerializer
