from django.urls import path
from apps.goods import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('details/<int:gid>', views.DetailsView.as_view(), name='detail'),
    # path('addcart/<int:gid>', views.AddCartView.as_view(), name='addcart')
]
