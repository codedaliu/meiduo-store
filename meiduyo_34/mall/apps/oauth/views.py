from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from mall import settings
from rest_framework import status

from oauth.models import OAuthQQUser
from oauth.serializer import OAuthQQUserSerializer
from oauth.utlis import generic_openid

"""
当用户点击QQ按钮的时候，会发送一个请求
我们后端返回一个url（URL是根据文档来拼接出来的）

GET    /oauth/qq/statues/
"""

class OauthQQURLAPIView(APIView):

    def get(self,request):

        # auth_url = 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101474184&redirect_uri=http://www.meiduo.site:8080/oauth_callback.html&state=abc'
        state = '/'
        #1 创建oauthqq的实例对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)
        #2 获取跳转的url
        auth_url = oauth.get_qq_url()

        return Response({'auth_url':auth_url})

"""
1 用户统一授权登录，这个时候会返回一个code
2 我们用code换取token
3 有了token,我们再获取openid
"""

"""
前端会接受到用户同意之后的 code 前端应该将这个code发送给后端

# 1 接受这个数据
# 2 用code换token
# 3 用token换openid

GET  /oauth/qq/users/?code=xxxxx
"""

class OAuthQQUserAPIView(APIView):

    def get(self,request):
        # 1 接受这个数据
        params = request.query_params
        code = params.get('code')
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2 用code换token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,)
        token = oauth.get_access_token(code)
        # '45EB90B33FFACB1F111678B56CC07093'
        # 3 用token换openid
        openid = oauth.get_open_id(token)
        """
        openid是此网站上唯一对应用户身份的标识，网站可将此ID进行存储便于用户下次登录时辨识其身份
        获取openid有两种情况
        1 用户之前绑定过
        2 用户之前没有绑定过
        """
        # 根据openid查询数据
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 不存在
            # openid很重要，所以我们需要对openid进行一个处理
            # 绑定也应该有一个时效
            #
            # s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
            # # 2 组织数据
            # data = {
            #     'openid': openid
            # }
            # # 3 让序列化器对数据进行处理
            # token = s.dumps(data)

            token = generic_openid(openid)

            return Response({'access_token':token})
        else:
            # 存在，让用户登录

            from rest_framework_jwt.settings import api_settings

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(qquser.user)
            token = jwt_encode_handler(payload)
            return Response({
                'token':token,
                'username':qquser.user.username,
                'user_id':qquser.user.id
            })
        # finally::


        # pass


    def post(self,request):
        # 1 接受数据
        data = request.data
        # 2 对数据进行校验
        serializer = OAuthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3 保存数据
        qquser = serializer.save()
        # 4 返回响应，应该有token
        from rest_framework_jwt.settings import api_settings

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(qquser.user)
        token = jwt_encode_handler(payload)
        return Response({
            'token': token,
            'username': qquser.user.username,
            'user_id': qquser.user.id
        })



"""
当用户点击绑定的时候，我们需要将手机号密码短信验证码和加密的openid传递过来

# 1 接受数据
# 2 对数据进行校验
# 3 保存数据
# 4 返回响应

POST    /oauth/qq/users/

"""




from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings
#1 创建一个序列化器
#secret_key 密钥
# expires_in=None  过期时间 单位是秒
s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
#2 组织数据
data = {
    'openid':'1234567890'
}
#3 让序列化器对数据进行处理
token = s.dumps(data)

#4 获取数据对数据进行解密
s.loads(token)