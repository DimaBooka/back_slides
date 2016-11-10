from django.conf.urls import url
from slides.views import LivePresentationView

urlpatterns = [
    url(r'^events-frame/(?P<pk>\d+)/live/$', LivePresentationView.as_view()),
]
