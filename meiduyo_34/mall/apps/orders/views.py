

"""
# 1 我们获取用户信息
# 2 从redis中获取数据
#   hash
#   set
# 3 需要获取的是选中的数据
# 4 [sku.id,sku.id]
# 5 [SKU,SKU,SKU]
# 6 返回响应

GET    /orders/placeorders/
"""
from decimal import Decimal
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import OrederSKUSerializer, OrderPlaceSerializer, OrderSerializer


class PlaceOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        # 1 我们获取用户信息
        user = request.user
        # 2 从redis中获取数据
        redis_conn = get_redis_connection('cart')
        #   hash
        redis_id_count = redis_conn.hgetall('cart_%s'%user.id)
        #   set
        selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)
        # 3 需要获取的是选中的数据
        # 同时对bytes类型进行转换
        selected_cart = {}

        for sku_id in selected_ids:

            selected_cart[int(sku_id)]=int(redis_id_count[sku_id])
        # 4 [sku.id,sku.id]
        ids = selected_cart.keys()
        # 5 [SKU,SKU,SKU]
        skus = SKU.objects.filter(pk__in=ids)

        for sku in skus:
            sku.count = selected_cart[sku.id]
        # 6 返回响应
        # serializer = OrederSKUSerializer(skus,many=True)

        # return Response(serializer.data)

        freight = Decimal('10.00')

        serializer = OrderPlaceSerializer({
            'freight':freight,
            'skus':skus
        })

        return Response(serializer.data)

"""
提交订单

1 接受前端数据(用户信息，地址信息，支付方式)
2 验证数据
3 数据入库
4 返回响应

POST   /orders/

"""
from rest_framework.generics import CreateAPIView
class OrderAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer






