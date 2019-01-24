from django.conf.urls import url
from . import views

# verifications/smscodes//?text=&image_code_id=
# http://127.0.0.1:8000/verifications/smscodes/15242969336/?text=&image_code_id=
urlpatterns = [
    url(r'^imagecodes/(?P<image_code_id>.+)/$',views.RegisterImageAPIView.as_view()),

    url(r'^smscodes/(?P<mobile>1[345789]\d{9})/$',views.RegisterSmscodeAPIView.as_view()),
]