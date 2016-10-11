from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()

router.register(r'presentations', views.PresentationViewSet)
router.register(r'events', views.EventViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^public_presentations/', views.PublicPresentationsList.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
