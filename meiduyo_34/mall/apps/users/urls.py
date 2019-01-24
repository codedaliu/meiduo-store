from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token


urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameAPIView.as_view()),
    url(r'^phones/(?P<mobile>1[345789]\d{9})/count/$',views.RegisterPhoneCountAPIView.as_view(),name='phonecount'),
    url(r'^$',views.RegiserUserAPIView.as_view()),
    # 实现登录
    # url(r'^auths/$',obtain_jwt_token),
    url(r'^auths/$', views.MergeLoginAPIView.as_view()),

    url(r'^infos/$',views.UserCenterInfoAPIView.as_view()),

    url(r'^emails/$',views.UserEmailInfoAPIView.as_view()),

    url(r'^emails/verification/$',views.UserEmailVerificationAPIView.as_view()),

    # url(r'^addresses/$',views.UserAddressAPIView.as_view()),

    # POST /users/browerhistories/
    url(r'^browerhistories/$',views.UserHistoryAPIView.as_view()),

]

"""
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.
eyJ1c2VybmFtZSI6Iml0Y2FzdCIsInVzZXJfaWQiOjUsImV4cCI6MTU0NzAzODg5NSwiZW1haWwiOiIifQ.
jA2ghdIvn5YCDvxCCIFELEKv-SuNS1Tg_P4mEHLioXM
"""
from .views import AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses',AddressViewSet,base_name='address')
urlpatterns += router.urls