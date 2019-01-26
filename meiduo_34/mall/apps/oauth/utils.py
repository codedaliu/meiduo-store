from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadSignature
from mall import settings


def generic_open_id(openid):

    # return openid

    #1.创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=60*60)
    #2. 对数据进行处理
    token = s.dumps({
        'openid':openid
    })
    #3.返回
    return token.decode()


def check_access_token(access_token):

    #1. 创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=60 * 60)
    #2. 对数据进行 loads操作
    try:
        data = s.loads(access_token)
        """
        data 就是当时设置的 字典
        {
            'openid':openid
        }
        """
    except BadSignature:
        return None
    #3.返回 openid
    return data['openid']

def generic_access_token(access_token):
    # 创建一个序列化器　secret_key秘钥
    # expires_in 过期时间　单位是秒
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    # 组织数据
    data = {
        'access_token': access_token
    }
    # ３．让序列化器对数据进行处理
    token = s.dumps(data)
    return token.decode()