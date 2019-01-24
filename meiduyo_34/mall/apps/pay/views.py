from django.shortcuts import render
from alipay import AliPay
# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mall import settings
from orders.models import OrderInfo
from pay.models import Payment

"""
1 第一步:创建应用(创建appid)
2 第二部:配置密钥(2对 我们的服务器一对,支付宝的一对)
    2.1 我们生成的公钥和私钥  私钥放在我们自己服务器上
        公钥放在支付宝的平台上
    2.2 把支付宝的公钥复制下来,需要放到一个以  ---public begin---  ---end---

3 第三部:搭建和配置开发环境(下载/安装SDK) (SDK就是支付宝封装好的库)
4 第四部:接口调用(开发,看支付宝的额API(接口文档))


"""

"""
当用户点击支付的时候 需要让前段将订单id传递过来

该接口必须是登陆用户

1 接收订单
2 根据订单id查询订单
3 生成alipay实力对象
4 调用时支付接口生成order_string
5 拼接url
5 返回url

GET /orders/(?P<order_id>\d+)/payment/
"""
from rest_framework.permissions import IsAuthenticated

class PaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        # 1 接收订单
        user = request.user
        # 2 根据订单id查询订单
        try:
            # 为了查询的准确性,我们尽量多加几个条件
            order = OrderInfo.objects.get(order_id=order_id,
                                           user=user,
                                           status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                                           )
        except OrderInfo.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3 生成alipay实力对象
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2", # RSA 或者 RSA2
        debug = settings.ALIPAY_DEBUG  # 默认False
        )
        # 4 调用时支付接口生成order_string
        subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),  # total_amount是decimal类型,要转换为str类型
            subject=subject,
            return_url="http://www.meiduo.site:8080/pay_success.html",
            # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        )
        # 5 拼接url
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        # 6 返回url
        return Response({'alipay_url':alipay_url})


"""
在支付页面,前段需要将支付宝返回的参数,提交给我们后端

我们后端进行验证,验证没有问题的话就获取支付宝id和我们的订单id
然后保存订单数据,同时修改订单的状态

put pay/status?xxxxx
"""

class PayStatuAPIView(APIView):

    def put(self,request):
        # 我们是让点券以查询字符串的形式传递过来的,
        # 1 获取参数
        data =request.query_params.dict()
        # sign不能参与签名验证
        signature = data.pop('sign')

        # 2 创建支付宝对象
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # verify
        success = alipay.verify(data.signature)
        if success:

            # 获取支付宝的id和我们的订单 id
            # out_trade_id我们的
            # trade_id 支付包的
            out_trade_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')

            Payment.objects.create(
                order_id=out_trade_id,
                trade_id=trade_id
            )

            # 修改订单状态
            OrderInfo.objects.filter(order_id=out_trade_id).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)