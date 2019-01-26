from django.conf.urls import url
from .views import OAuthQQURLAPIView,OAuthQQUserAPIView, OAuthSinaUserAPIView, OauthSinaURLAPIView

urlpatterns =[
    url(r'^qq/statues/$',OAuthQQURLAPIView.as_view()),

    url(r'^qq/users/$',OAuthQQUserAPIView.as_view()),

    url(r'^weibo/statues/$', OauthSinaURLAPIView.as_view()),
    url(r'^sina/user/$',OAuthSinaUserAPIView.as_view()),
]