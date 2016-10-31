from allauth.socialaccount.views import signup
from django.conf.urls import include, url
from django.contrib.auth.views import password_reset_confirm, password_reset_complete
from rest_framework.routers import DefaultRouter
from api.views import FacebookLogin, GoogleLogin, RegisterConfirmationView, PasswordReset, StartEvent, EndEvent

from api import views

router = DefaultRouter()

router.register(r'presentations', views.PresentationViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^reset/done/$', password_reset_complete, {'template_name': 'password-reset-done.html'}, name='password_reset_complete'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, {'template_name': 'password-reset-confirm.html'}, name='password_reset_confirm'),
    url(r'^rest-auth/password/reset/$', PasswordReset.as_view(),
        name='rest_password_reset'),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url('^signup/$', signup, name='socialaccount_signup'),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^rest-auth/google/$', GoogleLogin.as_view(), name='fb_login'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^account-confirm-email/(?P<key>[-:\w]+)/$', RegisterConfirmationView.as_view(),
        name='account_confirm_email'),
    url(r'^events/(?P<pk>\d+)/start/$', StartEvent.as_view()),
    url(r'^events/(?P<pk>\d+)/end/$', EndEvent.as_view()),
]
