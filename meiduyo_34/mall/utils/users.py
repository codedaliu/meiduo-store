import re

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }

from django.contrib.auth.backends import ModelBackend
from rest_framework.mixins import CreateModelMixin

"""
1 定义一个方法
2 把要抽取的代码复制过去，哪里有问题改哪里
3 验证
"""
def get_user_by_account(username):
    try:
        if re.match(r'1[3-9]\d{9}', username):
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user

class UsernameMobliModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        # 根据用户名确认用户输入的是手机号还是用户名
        # try:
        #     if re.match(r'1[3-9]\d{9}',username):
        #         user = User.objects.get(mobile = username)
        #     else:
        #         user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     user = None
        # # 验证用户密码
        user = get_user_by_account(username)

        if user is not None and user.check_password(password):
            return user
        # 必须要返回数据
        return None


class MyBackend(object):
    def authenticate(self,request,username=None,password=None):
        user = get_user_by_account(username)
        # 验证码用户密码
        if user is not None and user.check_password(password):
            return user
        # 必须要返回数据
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None