from django.shortcuts import render
from django.views.generic import View
from apps.user.models import Address
from utils.mixin import LoginRequiredMixin


# Create your views here.


class PlaceOrderView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        addr = Address.objects.get_default_address(user=user)
        context = {
            'addr': addr,
            'goods_li': ''
        }
        return render(request, 'order/place_order.html', context)
