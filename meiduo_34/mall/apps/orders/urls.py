from django.conf.urls import url
from . import views

urlpatterns = [
    #/orders/places/
    url(r'^places/$',views.PlaceOrderAPIView.as_view(),name='placeorder'),
    url(r'^$',views.OrderAPIView.as_view(),name='order'),
    url(r'^list/$', views.SKUOrderView.as_view()),



    url(r"^(?P<order_id>\d+)/uncommentgoods/$",views.UNcommentGoodsOrderAPIView.as_view(),name="uncommentgoods"),
    url(r"^(?P<order_id>\d+)/comments/$",views.CommentOrderAPIView.as_view(),name="comment"),
    url(r'^details/(?P<sku_id>\d+)/comments/$', views.CommentOrdersDeAPIView.as_view()),






]