from django.urls import path
from apps.goods import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('details/<int:gid>', views.DetailsView.as_view(), name='detail'),
    path('goodslist/<int:kid>', views.GoodsListView.as_view(), name='goods_list'),
    # path('addcart/<int:gid>', views.AddCartView.as_view(), name='addcart')
]
