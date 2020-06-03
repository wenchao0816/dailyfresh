from django.urls import path
from apps.goodscar.views import AddCartView, CartView, CartDeleteView

urlpatterns = [
    path('addcart/<int:gid>', AddCartView.as_view(), name='addcart'),
    path('cart', CartView.as_view(), name='cart'),
    path('cartdelete/<str:name>', CartDeleteView.as_view(), name='cartdelete')

]
