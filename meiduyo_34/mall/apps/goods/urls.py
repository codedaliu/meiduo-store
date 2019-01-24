from django.conf.urls import url
from . import views

urlpatterns = [
    #/goods/categories/(?P<category_id>\d+)/hotskus/
    url(r'^categories/(?P<category_id>\d+)/hotskus/$',views.HotSKUListAPIView.as_view(),name='hot'),

    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListAPIView.as_view()),

]