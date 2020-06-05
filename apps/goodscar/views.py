from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from utils.mixin import LoginRequiredMixin
from apps.goods.models import GoodsKinds, GoodsSKU
from utils.redis_connect import HashRedisConnect

# Create your views here.


class AddCartView(LoginRequiredMixin, View):

    def get(self, request, gid):
        conn = HashRedisConnect(request.user)
        if conn.get_cart(gid):
            # #TODO 后期处理
            pass
        else:
            conn.set_cart(gid, gid)
        return redirect(reverse('goods:detail', kwargs={'gid': gid}))


class CartView(LoginRequiredMixin, View):

    def get(self, request):
        kinds = GoodsKinds.objects.all()
        goods = HashRedisConnect(request.user).get_all_cart()
        goods_li = list()
        for unit_goods in goods:
            goods_details = GoodsSKU.objects.get(id=unit_goods)
            goods_details.num = goods[unit_goods].decode()
            goods_li.append(goods_details)
        context = {
            'goods_li': goods_li,
            'length': len(goods_li),
            'kinds': kinds
        }
        return render(request, 'goodscar/cart.html', context)


class CartDeleteView(LoginRequiredMixin, View):

    def get(self, request, goods_id):
        HashRedisConnect(request.user).del_cart(goods_id)
        return redirect(reverse('goodscar:cart'))
