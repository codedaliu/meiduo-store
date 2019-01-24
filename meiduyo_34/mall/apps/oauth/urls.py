from django.conf.urls import url
from .views import OauthQQURLAPIView,OAuthQQUserAPIView
urlpatterns = [
    url(r'^qq/statues/$',OauthQQURLAPIView.as_view()),
    url(r'^qq/users/$',OAuthQQUserAPIView.as_view()),
]