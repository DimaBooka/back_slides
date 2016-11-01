import django_filters
from django.db.models import Q

from rest_framework.filters import BaseFilterBackend

from django_filters import FilterSet
from slides.models import Presentation, Event, Commentary


class PresentationFilter(FilterSet):

    class Meta:
        model = Presentation
        fields = ('name', 'creator_id', 'date_created', 'published')


class EventFilter(FilterSet):
    date_finished_lte = django_filters.DateTimeFilter(name="date_finished", lookup_expr='lte')
    date_started_lte = django_filters.DateTimeFilter(name="date_started", lookup_expr='lte')
    date_planned_lte = django_filters.DateTimeFilter(name="date_planned", lookup_expr='lte')
    date_finished_gte = django_filters.DateTimeFilter(name="date_finished", lookup_expr='gte')
    date_started_gte = django_filters.DateTimeFilter(name="date_started", lookup_expr='gte')
    date_planned_gte = django_filters.DateTimeFilter(name="date_planned", lookup_expr='gte')

    class Meta:
        model = Event
        fields = ('author', 'name', 'presentation_id', 'date_planned', 'date_finished', 'date_started', 
                  'date_finished_lte', 'date_planned_lte', 'date_started_lte',
                  'date_finished_gte', 'date_planned_gte', 'date_started_gte')

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
