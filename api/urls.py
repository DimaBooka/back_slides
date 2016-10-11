from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from api import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$', views.api_root),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
urlpatterns += [url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))]
