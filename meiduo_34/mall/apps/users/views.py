import random

from django.shortcuts import render

# Create your views here.
from itsdangerous import BadData
from rest_framework.response import Response

# from mall.apps.users.models import User
# from apps.users.models import User
# from users.models import User
# 正确
from rest_framework.serializers import Serializer

from goods.models import SKU
from libs.yuntongxun.sms import CCP
from mall import settings

from users.models import User
from users.serialziers import RegiserUserSerializer, UserCenterInfoSerializer, UserEmailInfoSerializer, \
    AddressSerializer, AddUserBrowsingHistorySerializer, SKUSerializer
from users.utils import check_token
from utils.users import get_user_by_account

"""
1.分析需求 (到底要干什么)
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式
4.确定视图
5.按照步骤实现功能


 前端发送用户给后端 我们后端判断用户名 是否注册

 请求方式:
 GET        /users/usernames/(?P<username>\w{5,20})/count/

 # itcast 0
 # itcast 1

 POST


"""
#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#ListAPIVIew,RetriveAPIView     封装好了

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

class RegisterUsernameAPIView(APIView):

    def get(self,request,username):
        # 判断用户是否注册
        # 查询用户名的数量
        # itcast 0   没有注册
        # itcast 1   有注册

        count = User.objects.filter(username=username).count()

        # 返回数据
        return Response({'count':count,
                         'username':username})


"""

1.分析需求 (到底要干什么)
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式
4.确定视图
5.按照步骤实现功能

当用户点击注册按钮的时候 前端需要收集     手机号,用户名,密码,短信验证码,确认密码,是否同意协议

1. 接收数据
2. 校验数据
3. 数据入库
4. 返回相应

POST    /users/register/



"""
#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#CreateAPIView                  封装好了

class RegiserUserAPIView(APIView):

    def post(self,reqeust):
        # 1. 接收数据
        data = reqeust.data
        # 2. 校验数据
        serializer = RegiserUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3. 数据入库
        serializer.save()



        # 4. 返回相应
        # 序列化: 将模型转换为JSON
        # 如何序列化的呢? 我们的序列化器是根据字段来查询模型中的对应数据,如果 序列化器中有 模型中没有,则会报错
        # 如果字段设置为 write_only 则会在 序列化中 忽略此字段
        return Response(serializer.data)



"""
当用户注册成功之后,自动登陆

自动登陆的功能 是要求 用户注册成功之后,返回数据的时候
需要额外添加一个 token

1. 序列化的时候 添加token
2. token 怎么生成

"""




"""
个人中心的 信息展示
必须是登陆用户才可以访问

1. 让前端传递 用户信息
2. 我们根据用户的信息 来获取  user
3. 将对象转换为字典数据

GET     /users/infos/

"""
#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#ListAPIView,RetrieveAPIView     封装好了
from rest_framework.permissions import IsAuthenticated
# class UserCenterInfoAPIView(APIView):
#
#     # 添加 权限 必须是登陆用户才可以访问
#     permission_classes = [IsAuthenticated]
#
#     def get(self,request):
#
#         # 1.获取用户信息
#         user = request.user
#
#         #2. 将模型转换为字典(JSON)
#         serializer = UserCenterInfoSerializer(user)
#
#         #3.返回相应
#         return Response(serializer.data)

from rest_framework.generics import RetrieveAPIView
class UserCenterInfoAPIView(RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = UserCenterInfoSerializer

    # queryset = User.objects.all()

    # 已有的父类不能满足我们的需求
    def get_object(self):

        return self.request.user


"""
1.分析需求 (到底要干什么)
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式
4.确定视图
5.按照步骤实现功能

当用户 输入邮箱之后,点击保存的时候,
1.我们需要将 邮箱内容发送给后端,后端需要更新 指定用户的 email字段
2.同时后端需要给这个邮箱发送一个           激活连接
3.当用户点击激活连接的时候 ,改变 email_active的状态


用户 输入邮箱之后,点击保存的时候,
我们需要将 邮箱内容发送给后端

# 1. 后端需要接收 邮箱
# 2. 校验
# 3. 更新数据
# 4. 返回相应

PUT     /users/emails/


"""
#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#UpdateAPIView                   封装好了
# class UserEmailInfoAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#
#     def put(self,request):
#         # 1. 后端需要接收 邮箱
#         data = request.data
#         # 2. 校验
#         serializer = UserEmailInfoSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         # 3. 更新数据
#         serializer.save()
#          # 发送邮件
#         # 4. 返回相应
#         return Response(serializer.data)


from rest_framework.generics import UpdateAPIView


class UserEmailInfoAPIView(UpdateAPIView):
    # 权限,必须是登陆用户才可以访问此接口
    permission_classes = [IsAuthenticated]

    serializer_class = UserEmailInfoSerializer

    # 父类方法 不能满足我们的需求
    def get_object(self):

        return self.request.user



"""
激活需求:
当用户点击激活连接的时候,需要让前端接收到 token信息
然后让前端发送 一个请求,这个请求 包含  token信息

1. 接收token信息
2. 对token进行解析
3. 解析获取user_id之后,进行查询
4. 修改状态
5. 返回相应

GET     /users/emails/verification/


"""

#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#UpdateAPIView                   封装好了
from rest_framework import status
class UserEmailVerificationAPIView(APIView):

    def get(self,request):
        # 1. 接收token信息
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2. 对token进行解析
        user_id = check_token(token)


        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 解析获取user_id之后,进行查询
        user = User.objects.get(pk=user_id)
        # 4. 修改状态
        user.email_active=True
        user.save()
        # 5. 返回相应
        return Response({'msg':'ok'})



"""
1.分析需求 (到底要干什么)
2.把需要做的事情写下来(把思路梳理清楚)
3.路由和请求方式
4.确定视图
5.按照步骤实现功能

新增地址

1. 后端接收数据
2. 对数据进行校验
3. 数据入库
4. 返回相应

POST        /users/addresses/

"""
#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#CreateAPIView                   封装好了
# from rest_framework.generics import CreateAPIView
# from rest_framework.generics import GenericAPIView
#
# class UserAddressAPIView(CreateAPIView):
#
#     serializer_class = AddressSerializer

    # queryset =  新增数据用不到该属性

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from .serialziers import AddressTitleSerializer

class AddressViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    """
    用户地址新增与修改
    list GET: /users/addresses/
    create POST: /users/addresses/
    destroy DELETE: /users/addresses/
    action PUT: /users/addresses/pk/status/
    action PUT: /users/addresses/pk/title/
    """

    #制定序列化器
    serializer_class = AddressSerializer
    #添加用户权限
    permission_classes = [IsAuthenticated]
    #由于用户的地址有存在删除的状态,所以我们需要对数据进行筛选
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        count = request.user.addresses.count()
        if count >= 20:
            return Response({'message':'保存地址数量已经达到上限'},status=status.HTTP_400_BAD_REQUEST)

        return super().create(request,*args,**kwargs)

    def list(self, request, *args, **kwargs):
        """
        获取用户地址列表
        """
        # 获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        # 响应
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

"""

最近浏览记录
1. 必须是登陆用户的 我们才记录浏览记录
2. 在详情页面中添加 , 添加商品id 和用户id
3. 把数据保存在数据库中是每问题的
4. 我们把数据保存在redis的列表中 (回顾redis)


"""


"""
添加浏览记录的业务逻辑

1. 接收商品id
2. 校验数据
3. 数据保存到redis中
4. 返回相应

post    /users/histories/
"""

#APIView                        基类
#GenericAPIVIew                 对列表视图和详情视图做了通用支持,一般和mixin配合使用
#CreateAPIView                   封装好了
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin
from django_redis import get_redis_connection

class UserHistoryAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = AddUserBrowsingHistorySerializer

    # def get_serializer_class(self):
    #     if self.request.method == 'GET':

    # def get_queryset(self):
    #
    #     return

    """

    获取浏览记录数据

    # 1. 从redis中获取数据   [1,2,3]
    # 2. 根据id查询数据     [SKU,SKU,SKU]
    # 3. 使用序列化器转换数据
    # 4. 返回相应

    GET
    """
    def get(self,request):

        user = request.user

        # 1. 从redis中获取数据   [1,2,3]
        redis_conn = get_redis_connection('history')

        ids = redis_conn.lrange('history_%s'%user.id,0,4)
        # 2. 根据id查询数据     [SKU,SKU,SKU]
        # skus = SKU.objects.filter(id__in=ids)
        skus = []
        for id in ids:
            sku = SKU.objects.get(pk=id)
            skus.append(sku)

        # 3. 使用序列化器转换数据
        serializer = SKUSerializer(skus,many=True)
        # 4. 返回相应
        return Response(serializer.data)


from rest_framework_jwt.views import ObtainJSONWebToken
from carts.utils import merge_cookie_to_redis
class MergeLoginAPIView(ObtainJSONWebToken):


    def post(self, request, *args, **kwargs):
        # 调用jwt扩展的方法，对用户登录的数据进行验证
        response = super().post(request)

        # 如果用户登录成功，进行购物车数据合并
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 表示用户登录成功
            user = serializer.validated_data.get("user")
            # 合并购物车
            # merge_cart_cookie_to_redis(request, user, response)
            response = merge_cookie_to_redis(request, user, response)

        return response






# 忘记密码


# # 生成token
# def check_access_token(mobile):
#     # serializer = Serializer(秘钥, 有效期秒)
#     serializer = Serializer(settings.SECRET_KEY, 3600)
#     # serializer.dumps(数据), 返回bytes类型
#     token = serializer.dumps({'mobile': mobile})
#     token = token.decode()
#     return token
#
#
# # 校验token
# def inspect_access_token(token):
#     # 检验token
#     # 验证失败，会抛出itsdangerous.BadData异常
#     serializer = Serializer(settings.SECRET_KEY, 3600)
#     try:
#         data = serializer.loads(token)
#     except BadData:
#         return None
#     return data
#
#
#
# class FindUserPassword(APIView):
#     def get(self, reqeust, username):
#         try:
#             user = get_user_by_account(username)
#         except:
#             return Response('用户不存在')
#         user_mobile = user.mobile
#         text = reqeust.query_params.get('text')
#         image_id = reqeust.query_params.get('image_code_id')
#
#         redis_conn = get_redis_connection('code')
#         redis_text = redis_conn.get('img_' + str(image_id))
#
#         if redis_text.decode().lower() != text.lower():
#             raise Exception('输入错误')
#
#         token = check_access_token(mobile=user_mobile)
#
#         data = {
#             'mobile': user_mobile,  # 加密
#             'access_token': token,
#         }
#         return Response(data)
#
#
# class RegisterSMSCodeView(APIView):
#     def get(self, request):
#         access_token = request.query_params.get('access_token')
#
#         token = inspect_access_token(access_token)
#
#         mobile = token['mobile']
#
#         redis_conn = get_redis_connection('code')
#         sms_code = '%06d' % random.randint(0, 999999)
#         # redis增加记录
#         redis_conn.setex('sms_%s' % mobile, 5 * 60, sms_code)
#         redis_conn.setex('sms_flag_%s' % mobile, 60, 1)
#         # 发送短信
#         ccp = CCP()
#         ccp.send_template_sms(mobile, [sms_code, 5], 1)
#
#         return Response({'message': 'ok'})
#
#
# class SendPassword(APIView):
#     def get(self, request, username):
#
#         try:
#             user = get_user_by_account(username)
#         except:
#             return Response('用户不存在')
#
#         user_id = user.id
#
#         user_mobile = user.mobile
#
#         sms_code = request.query_params.get('sms_code')
#
#         redis_conn = get_redis_connection('code')
#
#         redis_code = redis_conn.get('sms_' + str(user_mobile)).decode()
#
#         if sms_code != redis_code:
#             raise Exception('验证码输入错误')
#
#         access_token = check_access_token(mobile=user_mobile)
#
#         data = {
#             'user_id': user_id,
#             'access_token': access_token
#         }
#
#         return Response(data)
#
#
# class CheakPassword(APIView):
#     def post(self, request, user_id):
#
#         password = request.data.get('password')
#         password2 = request.data.get('password2')
#         access_token = request.data.get('access_token')
#
#         if not access_token:
#             return Response('请求超时')
#         if password != password2:
#             return Response('前后密码不一致')
#
#         user = User.objects.get(id=user_id)
#         user.set_password(password)
#         user.save()
#         return Response(status=status.HTTP_201_CREATED)



from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings


# 生成token
def check_access_token(mobile):
    # serializer = Serializer(秘钥, 有效期秒)
    serializer = Serializer(settings.SECRET_KEY, 3600)
    # serializer.dumps(数据), 返回bytes类型
    token = serializer.dumps({'mobile': mobile})
    token = token.decode()
    return token


# 校验token
def inspect_access_token(token):
    # 检验token
    # 验证失败，会抛出itsdangerous.BadData异常
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    return data


#
# # 忘记密码的第一步图片验证码验证
class FindPassWordAPIView(APIView):
    # GET /users/17611666527/sms/token/?text=pokm&image_code_id=bec7e636-a811-4b48-9749-a7a54c7eda6d

    def get(self, request, username):
        try:
            user = get_user_by_account(username)
        except User.DoesNotExits:
            return Response({'message': '用户不存在'})
        text = request.query_params.get('text')
        image_id = request.query_params.get('image_code_id')
        # 连接redis对数据进行校验
        redis_conn = get_redis_connection('code')
        redis_text = redis_conn.get('img_' + str(image_id))
        if redis_text is None:
            return Response({'message': '图片验证码过期'})
        if redis_text.decode().lower() != text.lower():
            return Response({'message': '图片验证码错误'})
        access_token = check_access_token(mobile=username)
        mobile = user.mobile
        list = mobile[3:7]
        user_mobile = mobile.replace(list, '童童我儿')
        data = {
            'mobile': user_mobile,
            'access_token': access_token
        }
        return Response(data)


class GetTokenAPIView(APIView):
    '''发送短信，校验token'''

    def get(self, request):
        token = request.query_params.get('access_token')
        access_token = inspect_access_token(token)
        mobile = access_token['mobile']
        sms_code = '%06d' % random.randint(0, 999999)

        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_' + mobile, 5 * 60, sms_code)

        from clery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code)

        return Response({'message':'ok'})

class SendSmsAPIView(APIView):
    '''校验输入的短信验证码'''

    def get(self, request, username):

        '''
        校验手机号
        校验短信验证码
        校验access_token
        1, 获取前端传递过来的电话并进行验证
        2， 获取前端传递过来的短信验证码并链接redis进行校验
        3， 获取前端传递过来的access_token 进行校验
        4, 返回响应， user_id, access_token
        '''
        # 3， 获取前端传递过来的access_token 进行校验

            # 1, 获取前端传递过来的电话并进行验证
        try:
            user = get_user_by_account(username)
        except Exception as e:
            return Response('用户不存在')
        mobile = user.mobile
        # 2， 获取前端传递过来的短信验证码并链接redis进行校验
        sms_code = request.query_params.get('sms_code')
        redis_conn = get_redis_connection('code')
        smscode = redis_conn.get('sms_%s' % mobile).decode()
        if sms_code != smscode:
            return Response({'message': '短信验证码输入错误'})
        new_token = check_access_token(mobile=mobile)
        # 4, 返回响应， user_id, access_token
        data = {
            'user_id': user.id,
            'access_token': new_token
        }
        return Response(data)


class SetPassWordAPIView(APIView):
    def post(self, request, user_id):

        token = request.data.get('access_token')
        if inspect_access_token(token):
            return Response('token验证错误')
            # 获取user_id判断用户是否存在
        try:
            user = User.objects.get(user_id)
        except Exception as e:
            return Response('用户不存在')
        # 获取T /users/7/passwo前端传递过来的两个密码校验是否一致
        password = request.data.get('password')
        password2 = request.data.get('password2')
        if password != password2:
            return Response({'message': '两次输入的密码不一致'})
        user.set_password(password)
        user.save()
        return Response(status=status.HTTP_201_CREATED)
