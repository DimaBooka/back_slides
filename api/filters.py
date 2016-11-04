from django.db.models import Q

from rest_framework.filters import BaseFilterBackend

from django_filters import FilterSet
from slides.models import Presentation, Event, Commentary


class PresentationFilter(FilterSet):

    class Meta:
        model = Presentation
        fields = ('name', 'creator_id', 'date_created', 'published')


class EventFilter(FilterSet):
    class Meta:
        model = Event
        fields = {
            'author': ['exact'],
            'name': ['icontains'],
            'presentation_id': ['exact'],
            'date_planned': ['exact', 'lte', 'gte'],
            'date_finished': ['exact', 'lte', 'gte', 'isnull'],
            'date_started': ['exact', 'lte', 'gte', 'isnull'],
        }


class CommentaryFilter(FilterSet):

    class Meta:
        model = Commentary
        fields = ('presentation_id', 'date_created')


class PublishedPresentationFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        user = request.user

        if user.is_staff:
            return queryset

        return queryset.filter(
                Q(published=True) | (
                    Q(creator=user) if user.is_authenticated else Q()
                )
        )
