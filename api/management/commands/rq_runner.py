import django_rq
from api.cleaner import event_cleaner


queue = django_rq.get_queue('default')
queue.enqueue(event_cleaner)
worker = django_rq.get_worker()
worker.work()
event_cleaner.delay(86400)
