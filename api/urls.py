from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from api.views import FacebookLogin, GoogleLogin

from api import views

router = DefaultRouter()

router.register(r'presentations', views.PresentationViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^rest-auth/google/$', GoogleLogin.as_view(), name='fb_login'),
]
