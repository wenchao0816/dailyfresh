from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import JsonResponse
from utils.mixin import LoginRequiredMixin
from apps.goods.models import GoodsKinds, GoodsSKU
from utils.redis_connect import HashRedisConnect

# Create your views here.


class AddCartView(View):

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 199, 'errmsg': '用户未登录'})
        goods_id = request.POST.get('goods_id')
        count = request.POST.get('goods_num')
        if not all([goods_id, count]):
            return JsonResponse({'code': 201, 'errmsg': '商品信息不全面，请重新输入！'})
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 202, 'errmsg': '没有选择的商品信息，请核对后再次输入！'})
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'code': 203, 'errmsg': '商品数量类型有误，请核对后再次输入！'})
        # 注意验证商品库存是否充足
        if count > sku.stock:
            return JsonResponse({'code': 204, 'errmsg': '商品库存不足！'})
        conn = HashRedisConnect(request.user)
        goods_num = conn.get_cart(goods_id)
        if goods_num:
            goods_num = int(goods_num) + count
        else:
            goods_num = count
        conn.set_cart(goods_id, goods_num)
        goods_count = len(conn.get_all_cart())
        return JsonResponse({'code': 200, 'goods_count': goods_count, 'errmsg': '加入购物车成功！'})


class CartView(LoginRequiredMixin, View):

    def get(self, request):
        kinds = GoodsKinds.objects.all()
        goods = HashRedisConnect(request.user).get_all_cart()
        goods_li = list()
        total_count = 0
        total_amount = 0
        for unit_goods in goods:
            goods_details = GoodsSKU.objects.get(id=unit_goods)
            goods_details.num = goods[unit_goods].decode()
            goods_details.amount = goods_details.price * int(goods_details.num)
            total_count += int(goods_details.num)
            total_amount += goods_details.amount
            goods_li.append(goods_details)
        context = {
            'goods_li': goods_li,
            'length': len(goods_li),
            'kinds': kinds,
            'total_count': total_count,
            'total_amount': total_amount
        }
        return render(request, 'goodscar/cart.html', context)


class UpdateView(View):

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 199, 'errmsg': '用户未登录'})
        goods_id = request.POST.get('goods_id')
        goods_num = request.POST.get('goods_num')
        if not all([goods_id, goods_num]):
            return JsonResponse({'code': 201, 'errmsg': '商品信息不全面，请重新输入！'})
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 202, 'errmsg': '没有选择的商品信息，请核对后再次输入！'})
        try:
            goods_num = int(goods_num)
        except Exception as e:
            return JsonResponse({'code': 203, 'errmsg': '商品数量类型有误，请核对后再次输入！'})
        # 注意验证商品库存是否充足
        if goods_num > sku.stock:
            return JsonResponse({'code': 204, 'goods_num': sku.stock, 'errmsg': '商品库存不足！'})
        conn = HashRedisConnect(request.user)
        conn.set_cart(goods_id, goods_num)
        return JsonResponse({'code': 200, 'errmsg': '加入购物车成功！'})


class DeleteView(View):

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'code': 201, 'errmsg': '用户未登录！'})
        goods_id = request.POST.get('goods_id')
        HashRedisConnect(request.user).del_cart(goods_id)
        return JsonResponse({'code': 200, 'msg': '商品信息删除成功！'})
