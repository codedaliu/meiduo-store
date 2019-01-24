import random

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from libs.yuntongxun.sms import CCP
from verifications.serializers import RegisterSmscodeSerializer
from clery_tasks.sms.tasks import send_sms_code

"""
1 分析需求，到底要干什么
2 把需要做的事情写下来
3 请求方式和路由
4 确定视图
5 按照步骤实现功能

前端传递一个uuid过来，后端生成一个图片

1 接受image_code_id
2 生成图片和验证码
3 把验证码保存到redis中
4 返回图片响应
5 确定请求方式
6 确定路由    /verifications/imagecodes/(?P<image_code_id>.+)/
"""

class RegisterImageAPIView(APIView):

    def get(self,request,image_code_id):
        # print(image_code_id)
        #1 接收image_code_id
        #2 生成图片和验证码
        text,image = captcha.generate_captcha()
        #3 把验证码保存到redis中
        #3.1 链接redis
        redis_conn = get_redis_connection('code')
        #3.2 设置图片
        redis_conn.setex('img_'+image_code_id,600,text)
        #4 返回图片响应
        return HttpResponse(image,content_type='image/jpeg')


"""
1 分析需求，到底要干什么
2 把需要做的事情写下来
3 请求方式和路由
4 确定视图
5 按照步骤实现功能

当用户点击获取短信按钮的时候 前端应该将手机号，图片验证码以及验证码id发送给后端

# 1 接受参数
# 2 校验参数
# 3 生成短信
# 4 将短信保存在redis中
# 5 使用运通讯发送短信
# 6 返回响应

GET  一种是路由，一种是查询字符串，混合起来也可以


"""
# class RegisterSmscodeAPIView(APIView):
#
#     def get(self,request,mobile):
#         # 1 接受参数
#         params = request.query_params
#         # 2 校验参数，还需要验证码 用户输入的图片验证码和redis的保存是否一致
#         serializer = RegisterSmscodeSerializer(data=params)
#         serializer.is_valid(raise_exception=True)
#         # 3 生成短信
#         sms_code = '%06d'%random.randint(0,999999)
#         # 4 将短信保存在redis中
#         redis_conn = get_redis_connection('code')
#         redis_conn.setex('sms_'+mobile,5*60,sms_code)
#         # 5 使用运通讯发送短信
#         # CCP().send_template_sms(mobile,[sms_code,5],'1')
#         # from clery_tasks.sms.tasks import send_sms_code
#         # # delay的参数和任务的参数对应
#         # # 必须调用delay方法
#         # send_sms_code.delay(mobile,sms_code)
#         from clery_tasks.sms.tasks import send_sms_code
#         # delay 的参数和 任务的参数对应
#         # 必须调用 delay 方法
#         send_sms_code.delay(mobile,sms_code)
#         # 6 返回响应
#         return Response({'msg':'ok'})

        #########################################################

class RegisterSmscodeAPIView(APIView):

    def get(self,request,mobile):
        # 1.接收参数
        params = request.query_params
        # 2.校验参数  还需要验证码 用户输入的图片验证码和redis的保存 是否一致
        serializer = RegisterSmscodeSerializer(data=params)
        serializer.is_valid(raise_exception=True)
        # 3.生成短信
        sms_code = '%06d'%random.randint(0,999999)
        # 4.将短信保存在redis中
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_'+mobile,5*60,sms_code)
        # 5.使用云通讯发送短信
        CCP().send_template_sms(mobile,[sms_code,5],1)

        # from clery_tasks.sms.tasks import send_sms_code
        # delay 的参数和 任务的参数对应
        # 必须调用 delay 方法
        # send_sms_code.delay(mobile,sms_code)
        #
        # 6.返回相应
        return Response({'msg':'ok'})

        """
        写信
        投递到邮箱

        """
