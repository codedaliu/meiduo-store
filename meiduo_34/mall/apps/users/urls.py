from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    #/users/usernames/(?P<username>\w{5,20})/count/
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameAPIView.as_view(),name='usernamecount'),

    url(r'^$',views.RegiserUserAPIView.as_view()),

    #实现登陆
    # url(r'^auths/',obtain_jwt_token),
    url(r'^auths/',views.MergeLoginAPIView.as_view()),
    # jwt 把用户名和密码给系统,让系统进行认证,认证成功之后jwt 生成token

    #
    url(r'^infos/$',views.UserCenterInfoAPIView.as_view()),

    # users/emails/
    url(r'^emails/$',views.UserEmailInfoAPIView.as_view()),

    url(r'^emails/verification/$',views.UserEmailVerificationAPIView.as_view()),


    # url(r'^addresses/$',views.UserAddressAPIView.as_view()),

    #/users/browerhistories/
    url(r'^browerhistories/$',views.UserHistoryAPIView.as_view()),







    url(r'(?P<user_pwd>\d+)/password/$', views.UserPassWordView.as_view()),
    #忘记密码

    url(r'^(?P<username>1[345789]\d{9})/sms/token/$', views.FindPassWordAPIView.as_view()),
    url(r'^sms_codes/$', views.GetTokenAPIView.as_view()),
    url(r'^(?P<username>1[345789]\d{9})/password/token/$', views.SendSmsAPIView.as_view()),
    url(r'^(?P<user_id>\d+)/password/$', views.SetPassWordAPIView.as_view()),
>>>>>>> d0498be2c2b6d3bc6e8b4833e1e721545c6a3c73

]

from .views import AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses',AddressViewSet,base_name='address')
urlpatterns += router.urls


"""
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.
eyJ1c2VybmFtZSI6Iml0Y2FzdCIsImV4cCI6MTU0NzAwMDQxNCwiZW1haWwiOiIiLCJ1c2VyX2lkIjo4fQ.
HVw9FkI7gXxobEtMWJ9t4QXsBbV54l4rA5ehddwqnZ4
"""