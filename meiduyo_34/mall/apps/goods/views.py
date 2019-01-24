from django.shortcuts import render

# Create your views here.
from goods.models import SKU
from goods.serializer import HotSKUListSerializer

"""
表单的设计　思想：
１　根据产品给的类型　尽量多的分析表的字段　不要分析表和表之间的关系
２　在一个没人安静的地方分析表与表之间的关系

"""

"""
页面静态化

其实就是先把数据查询出来，出来之后将数据填充到模板中，
形成了html，将html写入到指定的文件

当用户访问的时候，直接访问　静态html
"""


"""
列表数据
一个是热销数据: 应该是到哪个分类去　获取哪个分类的热销数据
一个是列表数据：　
１　获取分类id
２　根据id获取数据
３　将数据转换为json数据
４　返回响应

GET  /goods/categories/(?P<category_id>\d+)/hotskus/
"""
from rest_framework.generics import ListAPIView
class HotSKUListAPIView(ListAPIView):
    # 设置不分页
    pagination_class = None

    # queryset = SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id).order_by('-sales')[:2]

    serializer_class = HotSKUListSerializer



"""
列表数据的获取

当用户选择一个分类的时候，我们需要对分类数据进行排序，进行分页处理

简化需求，一步一步的实现

先获取所有分类数据，再排序，在分页

1.先获取所有数据　　[SKU,SKU,SKU]
2.将对象列表转换为字典
3.返回响应

GET  /goods/categories/(?P<category_id>\d+)/hotskus/

"""
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
from rest_framework.generics import GenericAPIView
class SKUListAPIView(ListAPIView):

    # 添加排序
    filter_backends = [OrderingFilter]
    ordering_fields = ['create_time','sales','price']

    # 只为当前视图设置分页
    # pagination_class =

    serializer_class = HotSKUListSerializer

    # queryset = SKU.objects.filter(category=category_id)
    def get_queryset(self):

        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category=category_id)

