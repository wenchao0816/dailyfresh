from django.urls import path
from apps.order.views import PlaceOrderView, GenerateOrderView, PayOrderView, CheckOrderView

urlpatterns = [
    path('place', PlaceOrderView.as_view(), name='place'),
    path('generate', GenerateOrderView.as_view(), name='generate'),
    path('pay', PayOrderView.as_view(), name='pay'),
    path('check', CheckOrderView.as_view())
]
