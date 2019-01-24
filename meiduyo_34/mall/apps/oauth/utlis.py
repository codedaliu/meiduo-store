from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature
from mall import settings
def generic_openid(openid):
    # 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=60*60)
    # 对数据进行处理
    token = s.dumps({
        'openid':openid
    })
    return token.decode()

def check_access_token(access_token):

    #1 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=60 * 60)
    #2 对数据进行loads操作
    try:
        data = s.loads(access_token)
        """
        data 就是当时设置的字典
        {
            'openid':openid
        }
        """
    except BadSignature:
        return None
    #3 返回openid
    return data['openid']
