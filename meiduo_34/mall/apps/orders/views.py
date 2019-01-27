from decimal import Decimal
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.models import OrderGoods, OrderInfo
from orders.serializers import OrderSKUSerialzier, OrderPlaceSerializer, OrderSerializer, CommentOrderSerializer, \
    UserSkuOrderGoodsSerializer, CommentOrdersDeSerializer,  UserOrderGoodsSerializer

from apps.orders.serializers import UserOrdersSerializer

"""
订单列表展示

必须是登陆用户才可以访问

# 1. 我们获取用户信息
# 2. 从redis中获取数据
#     hash
#     set
# 3. 需要获取的是 选中的数据
# 4. [sku_id,sku_id]
# 5. [SKU,SKU,SKU]
# 6. 返回相应

GET     /orders/placeorders/


"""
from rest_framework.permissions import IsAuthenticated
class PlaceOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        # 1. 我们获取用户信息
        user = request.user
        # 2. 从redis中获取数据
        redis_conn = get_redis_connection('cart')
        #     hash
        redis_id_count = redis_conn.hgetall('cart_%s'%user.id)
        # {b'sku_id':b'count'}
        #     set
        selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

        # [b'sku_id']
        # 3. 需要获取的是 选中的数据
        # 同时对bytes类型进行转换
        selected_cart = {}   # {sku_id:count}

        for sku_id in selected_ids:

            selected_cart[int(sku_id)]=int(redis_id_count[sku_id])


        # {1:5,3:20}
        # 4. [sku_id,sku_id]
        ids = selected_cart.keys()
        # 5. [SKU,SKU,SKU]
        skus = SKU.objects.filter(pk__in=ids)

        for sku in skus:
            sku.count = selected_cart[sku.id]
        # 6. 返回相应
        # serializer = OrderSKUSerialzier(skus,many=True)

        # data = {
        #     'freight':10,
        #     'skus':serializer.data
        # }
        #
        # return Response(data)

        # return Response(serializer.data)

        freight = Decimal('10.00')

        serializer = OrderPlaceSerializer({
            'freight':freight,
            'skus':skus
        })


        return Response(serializer.data)


"""

提交订单

1. 接收前端数据 (用户信息,地址信息,支付方式)
2. 验证数据
3. 数据入库
4. 返回相应

POST    /orders/

"""
from rest_framework.generics import CreateAPIView, ListAPIView


class OrderAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer


class SKUOrderView(ListAPIView):

    # pagination_class = LargeResultsSetPagination
    # pagination_class = StandardResultsSetPagination

    permission_classes = [IsAuthenticated]

    serializer_class = UserOrdersSerializer

    def get_queryset(self):
        user = self.request.user
        orders = user.orderinfo_set.all()
        return orders

























class UNcommentGoodsOrderAPIView(ListAPIView):

    # permission_classes = [IsAuthenticated]

    pagination_class = None


    serializer_class = UserOrderGoodsSerializer



    def get_queryset(self):
        order_id = self.kwargs.get("order_id")

        return OrderGoods.objects.filter(order_id=order_id,is_commented= False,)




class CommentOrderAPIView(APIView):

    # permission_classes = [IsAuthenticated]
    pagination_class = None

    def post(self,request,order_id):

        # 1.接受数据
        data = request.data
        # 2.校验数据
        serializer = CommentOrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        order = serializer.validated_data.get('order')
        sku = serializer.validated_data.get('sku')
        comment = serializer.validated_data.get('comment')
        score = serializer.validated_data.get('score')
        is_anonymous = serializer.validated_data.get('is_anonymous')

        # 3. 数据入库
        try:
            comment_goods = OrderGoods.objects.get(order = order, sku = sku)
        except OrderGoods.DoesNotExist:
            return Response({'message': '产品信息有误'}, status=status.HTTP_400_BAD_REQUEST)

        comment_goods.comment = comment
        comment_goods.score = score
        comment_goods.is_anonymous = is_anonymous
        comment_goods.is_commented = True
        comment_goods.save()

        # 判断订单状态
        try:
            flag = 0
            comments_goods = OrderGoods.objects.filter(order_id=order_id)
            for comment_good in comments_goods:
                if comment_good.is_commented == False:
                    flag = 1
            if flag == 0:
                try:
                    comment_infos =  OrderInfo.objects.get(order_id=order_id)
                except OrderInfo.DoesNotExist:
                    return Response({'message': '产品信息错误'}, status=status.HTTP_400_BAD_REQUEST)
                comment_infos.status = 5
                comment_infos.save()
        except OrderGoods.DoesNotExist:
            return Response({'message': '产品信息错误'}, status=status.HTTP_400_BAD_REQUEST)

            # 4. 返回相应
        return Response({
            'comment': comment,
            'score': score,
            'is_anonymous': is_anonymous,

        })

        # 详情展示

class CommentOrdersDeAPIView(ListAPIView):

        # 评论详情数据
        # GET /orders/(?P<sku_id>\d+)/comments/

        pagination_class = None

        def get_queryset(self):
            sku_id = self.kwargs.get('sku_id')
            return OrderGoods.objects.filter(sku_id=sku_id, is_commented=True)

        serializer_class = CommentOrdersDeSerializer