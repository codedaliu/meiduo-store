from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.utils import merge_cookie_to_redis
from goods.models import SKU
from users.models import User
from users.serialziers import RegiserUserSerializer, UserCenterInfoSerlalizer, UserEmailInfoSerializer, \
    AddressSerializer, AddUserBrowsingHistorySerializer, SKUSerializer
from users.utils import check_token

"""
1 分析需求（到底要干什么）
2 把需要做的事情写下来(把思路梳理清楚)
3 确定路由和请求方式
4 确定视图
5 按照步骤实现功能


前端发送用户给后端 我们后端判断用户名是否注册

请求方式
GET    /users/usernames/(?P<username>\w{5,20})/count/

# itcast 0
# itcast 1

POST

"""

class RegisterUsernameAPIView(APIView):
    '''获取用户名的个数
        GET:  /users/usernames/(?P<username>\w{5,20})/count/
    '''

    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        print(username)
        context = {
            'count':count,
            'username':username,
        }

        return Response(context)

class RegisterPhoneCountAPIView(APIView):
    """
    查询手机号的个数
    GET

    """
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        context = {
            'count':count,
            'phone':mobile,
        }
        return Response(context)

"""
当用户点击注册按钮的时候 前端需要收集手机号，用户名，密码，短信验证码，确认密码是否同意
# 1 接受数据
# 2 校验数据
# 3 数据入库
# 4 返回响应
POST  /users/register
"""
class RegiserUserAPIView(APIView):

    def post(self,request):
        # 1 接受数据
        data = request.data
        # 2 校验数据
        serializer = RegiserUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3 数据入库
        serializer.save()

        # 4 返回响应
        # 序列化：将模型转换为json
        return Response(serializer.data)

"""
当用户注册成功之后，自动登录

自动登录的功能 是要求 用户注册成功之后，返回数据的时候需要额外添加一个token

1 序列化的时候添加 token
2 token怎么生成
"""


"""
个人中心的信息展示
必须是登录用户才可以访问

1 让前端传递用户信息
2 我们根据用户的信息来获取 user
3 将对象转换为字典数据

GET /users/infos/user_id/
"""
from rest_framework.permissions import IsAuthenticated
# class UserCenterInfoAPIView(APIView)
#
#     # 添加 权限 必须是登录用户才可以访问
#     permission_classes = [IsAuthenticated]
#
#     def get(self,request):
#         # 1 获取用户信息
#         user = request.user
#         # 2 将模型转换为字典
#         serializer = UserCenterInfoSerlalizer(user)
#         # 3 返回响应
#         return Response(serializer.data)

from rest_framework.generics import RetrieveAPIView
class UserCenterInfoAPIView(RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = UserCenterInfoSerlalizer

    # 以有的父类不能满足我们的需求
    def get_object(self):

        return self.request.user


"""
当用户输入邮箱之后，点击保存的时候，
1 我们需要将邮箱内容发送给后端，后端需要更新指定用户的email字段
2 同时后端需要给这个邮箱发送一个激活连接
3 当用户点击激活链接的时候， 改变email_active的状态

用户输入邮箱之后，点击保存的时候
我们需要将邮箱内容发送给后端

1 后端需要接受邮箱
2 校验
3 更新数据
4 返回响应

PUT    /users/emails/

"""
# class UserEmailInfoAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#
#     def put(self,request):
#         # 1 后端需要接受邮箱
#         data = request.data
#         # 2 校验
#         serializer = UserEmailInfoSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         # 3 更新数据
#         serializer.save()
#         # 4 返回响应
#         return Response(serializer.data)
from rest_framework.generics import UpdateAPIView
class UserEmailInfoAPIView(UpdateAPIView):
    # 权限必须是登录用户才可以访问此接口
    permission_classes = [IsAuthenticated]

    serializer_class = UserEmailInfoSerializer

    # 父类方法不能满足我们的需求
    def get_object(self):

        return self.request.user

"""
激活需求：
当用户点击激活链接的时候，需要让前端接受到token信息
然后让前端发送一个请求，这个请求包含 token信息

1 接受token信息
2 对token进行解析
3 解析后对user_id后 进行查询
4 修改状态
5 返回响应

GET    /users/emails/verification/


"""
from rest_framework import status
from django_redis import get_redis_connection
class UserEmailVerificationAPIView(APIView):

    def get(self,request):
        # 1 接受token信息
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2 对token进行解析
        user_id = check_token(token)
        if user_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3 解析后对user_id后 进行查询
        user = User.objects.get(pk=user_id)
        # 4 修改状态
        user.email_active=True
        user.save()
        # 5 返回响应
        return Response({'msg':'ok'})


"""
新增地址
１　前端提交数据
２　后端接受数据
３　对数据进行校验
４　数据入库
５　返回响应

POST    /user/addresses/
"""
from rest_framework.generics import CreateAPIView


class UserAddressAPIView(CreateAPIView):

    serializer_class = AddUserBrowsingHistorySerializer


"""
最近浏览记录
１　必须是登录用户的　我们才记录浏览记录
２　在详情页面中添加商品id和用户id
3  把数据保存在redis的列表中

"""

"""
添加浏览记录的业务逻辑

１　接受商品id
2  校验数据
３　数据保存到redis中
４　返回响应

post     /users/histories/
"""
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin
class UserHistoryAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = AddUserBrowsingHistorySerializer

    """
    获取浏览记录数据
    1 从redis中获取数据  [1,2,3]
    2 根据id查询数据　　　
    3 使用序列化器转换数据
    4 返回响应
    """
    def get(self,request):

        user = request.user

        # 1 从redis中获取数据  [1,2,3]
        redis_conn = get_redis_connection('history')

        ids = redis_conn.lrange('history_%s'%user.id,0,4)
        # 2 根据id查询数据　　　
        # skus = SKU.objects.filter(id__in=ids)
        skus = []
        for id in ids:
            sku = SKU.objects.get(pk=id)

            skus.append(sku)
        # 3 使用序列化器转换数据
        serializer = SKUSerializer(skus,many=True)
        # 4 返回响应
        return Response(serializer.data)

from rest_framework_jwt.views import ObtainJSONWebToken
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



"""
新增地址
1 后端接受数据
2 对数据进行校验
3 数据入库
4 返回响应

POST /users/addresses/
"""
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
    # 制定序列化器
    serializer_class = AddressSerializer
    # 添加用户权限
    permission_classes = [IsAuthenticated]
    #由于用户的地址有存在删除的hangtag，所以我们需要对数据进行筛选
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self,request, *args, **kwargs):
        """
        保存用户地址数据
        """
        count = request.user.addresses.count()
        if count >= 20:
            return Response({'message':'保存地址数量已经达到上限'},status=status.HTTP_400_BAD_REQUEST)

        return super().create(request,*args,**kwargs)

    def list(self,request,*args,**kwargs):
        """
        获取用户地址列表
        """
        # 获取所有地址
        queryset = self.get_queryset()
        # 创建序列化器
        serializer = self.get_serializer(queryset,many=True)
        user = self.request.user
        # 响应
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def destroy(self,request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()
        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def title(self,request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address,data=request.data)
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
        return Response({'message':'OK'},status=status.HTTP_200_OK)