from django.conf.urls import include, url

from chat.views import chat

urlpatterns = [
    url(r'^chat/', view=chat),
]
