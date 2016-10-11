from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

from api import views

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^presentations/', views.PublicPresentationsList.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]