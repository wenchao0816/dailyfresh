from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from apps.goods import models

# Create your views here.


class AddCartView(LoginRequiredMixin, View):

    def get(self, request, gid):
        user = request.user
        gname = models.GoodsSKU.objects.get(id=gid)
        cart_key = 'cart_key_%d' % user.id
        conn = get_redis_connection('default')
        conn.hset(cart_key, gname.id, gid)
        return redirect(reverse('goods:detail', kwargs={'gid': gid}))


class CartView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        cart_key = 'cart_key_%d' % user.id
        conn = get_redis_connection('default')
        goods = conn.hgetall(cart_key)
        goods_li = list()
        for unit_goods in goods:
            unit_goods = unit_goods.decode()
            goods_details = models.GoodsSKU.objects.get(goods_name=unit_goods)
            goods_li.append(goods_details)
        return render(request, 'goodscar/cart.html', {'goods_li': goods_li, 'goods_dic': goods})


class CartDeleteView(View):

    def get(self, request, name):
        user = request.user
        cart_key = 'cart_key_%d' % user.id
        conn = get_redis_connection('default')
        conn.hdel(cart_key, name)
        return redirect(reverse('goodscar:cart'))
