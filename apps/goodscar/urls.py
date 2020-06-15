from django.urls import path
from apps.goodscar.views import AddCartView, CartView, DeleteView, UpdateView

urlpatterns = [
    path('addcart', AddCartView.as_view(), name='addcart'),
    path('cart', CartView.as_view(), name='cart'),
    path('delete', DeleteView.as_view(), name='delete'),
    path('update', UpdateView.as_view(), name='update')
]
