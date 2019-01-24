from django.shortcuts import render

# Create your views here.
from areas.models import Area
from areas.serializer import AreaSerializer, SubsAreaSerialzier

"""


"""

from rest_framework.viewsets import ReadOnlyModelViewSet
#　缓存
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework_extensions.cache.mixins import RetrieveCacheResponseMixin
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AreaModelViewSet(CacheResponseMixin,ReadOnlyModelViewSet):

    # 让它不使用分页类，在视图里设置的属性比在settings里设置属性的权限高
    pagination_class = None

    # queryset = Area.objects.all()
    # queryset = Area.objects.filter(parent_id__null=True)
    #
    # serializer_class = AreaSerializer
    def get_queryset(self):
        # 我们可以根据不不同的业务逻辑返回不同的数据源
        if self.action == 'list':
            # Area.objects.filter(parent__isnull=True)
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):

        # 我们可以根据不同的业务逻辑返回不同的序列化器
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsAreaSerialzier


