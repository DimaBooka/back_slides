import django
import redis
from django.conf import settings
from django.utils.timezone import now
from rq.decorators import job
django.setup()

from slides.models import Event

redis_con = redis.from_url(settings.REDIS_CON)


@job('default', connection=redis_con)
def event_cleaner():
    print('kek')
    Event.objects.filter(date_planned__lt=now()).exclude(date_started__isnull=False).update(date_finished=now())
