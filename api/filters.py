from django_filters import FilterSet
from slides.models import Presentation, Event, Commentary


class PresentationFilter(FilterSet):

    class Meta:
        model = Presentation
        fields = ('name', 'creator__username', 'date_created', 'published')


class EventFilter(FilterSet):

    class Meta:
        model = Event
        fields = ('name', 'presentation__name', 'date', 'state')


class CommentaryFilter(FilterSet):

    class Meta:
        model = Commentary
        fields = ('presentation__name', 'date_created')
