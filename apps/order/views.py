from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views.generic import View
from django.http import JsonResponse
from django.db import transaction
from apps.user.models import Address
from apps.goods.models import GoodsSKU
from apps.order.models import OrderInfo, OrderGoods
from utils.mixin import LoginRequiredMixin
from utils.redis_connect import HashRedisConnect
from utils.alipay import client
import time
import json

from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.domain.SettleDetailInfo import SettleDetailInfo
from alipay.aop.api.domain.SettleInfo import SettleInfo
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
# Create your views here.


class PlaceOrderView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        addrs = Address.objects.filter(user=user)
        goods_id = request.GET.get('goods_id')
        skus = ','.join(goods_id)
        if not goods_id:
            return redirect(reverse('goodscar:cart'))
        total_count = 0
        total_amount = 0
        goods_li = list()
        conn = HashRedisConnect(user)
        try:
            goods = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:details')+'/1')
        goods.count = conn.get_cart(goods_id).decode()
        total_count += int(goods.count)
        goods.amount = goods.price * int(goods.count)
        total_amount += goods.amount
        goods_li.append(goods)
        context = {
            'addrs': addrs,
            'goods_li': goods_li,
            'total_count': total_count,
            'total_amount': total_amount,
            'skus': skus
        }
        return render(request, 'order/place_order.html', context)

    def post(self, request):
        user = request.user
        addrs = Address.objects.filter(user=user)
        goods_ids = request.POST.getlist('goods_ids')
        if not goods_ids:
            return redirect(reverse('goodscar:cart'))
        skus = ','.join(goods_ids)
        goods_li = list()
        total_count = 0
        total_amount = 0
        conn = HashRedisConnect(user)
        for goods_id in goods_ids:
            try:
                goods = GoodsSKU.objects.get(id=goods_id)
            except GoodsSKU.DoesNotExist:
                return redirect(reverse('goodscar:cart'))
            goods.count = conn.get_cart(goods_id).decode()
            total_count += int(goods.count)
            goods.amount = goods.price * int(goods.count)
            total_amount += goods.amount
            goods_li.append(goods)
        context = {
            'addrs': addrs,
            'goods_li': goods_li,
            'total_count': total_count,
            'total_amount': total_amount,
            'skus': skus
        }
        return render(request, 'order/place_order.html', context)


class GenerateOrderView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'code': 201, 'errmsg': '用户未登录！'})
        addr_id = request.POST.get('receive_addr')
        pay_style = request.POST.get('pay_style')
        skus = request.POST.get('skus')
        if not all([addr_id, pay_style]):
            return JsonResponse({'code': 202, 'errmsg': '订单提交信息不完整，请核对后再次提交'})
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 203, 'errmsg': '订单地址不存在，请核对后再次提交'})
        if not OrderInfo.PAY_CHOICES[int(pay_style)][int(pay_style)]:
            return JsonResponse({'code': 204, 'errmsg': '选择的支付方式有误，请核对后再次提交'})
        order_id = time.strftime('%Y%m%d%H%M%S')+str(user.id)
        total_amount = 0
        total_money = 0
        freight = 10
        pay_status = 0
        save01 = transaction.savepoint()
        order = OrderInfo.objects.create(
                    order_id=order_id,
                    address=addr,
                    user=user,
                    pay_ways=pay_style,
                    amount=total_amount,
                    total_money=total_money,
                    freight=freight,
                    pay_status=pay_status
                )
        conn = HashRedisConnect(user)
        skus = skus.split(',')
        for sku_id in skus:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                transaction.savepoint_rollback(save01)
                return JsonResponse({'code': 205, 'errmsg': '提交商品信息有误，请核对后再次提交'})
            count = conn.get_cart(sku.id)
            total_amount += int(count)
            total_money += sku.price * int(count)
            if int(count) > sku.stock:
                transaction.savepoint_rollback(save01)
                return JsonResponse({'code': 206, 'errmsg': '商品库存不足，已通知工作人员尽快补货！'})
            OrderGoods.objects.create(
                order=order,
                SKU=sku,
                goods_amount=int(count),
                price=sku.price,
                comment=''
            )
            conn.del_cart(sku.id)
        order.total_money = total_money
        order.amount = total_amount
        order.save()
        transaction.savepoint_commit(save01)
        return JsonResponse({'code': 200, 'msg': '创建订单成功！'})


class PayOrderView(View):

    def post(self, request):

        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'code': 201, 'errmsg': '用户未登录！'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'code': 202, 'errmsg': '未获取到有效订单号，请核对后再次提交！'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_status=0)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 203, 'errmsg': '未查询到该用户的有效订单，请核对后再次提交！'})

        # logging.basicConfig(
        #     level=logging.INFO,
        #     format='%(asctime)s %(levelname)s %(message)s',
        #     filemode='a', )
        # logger = logging.getLogger('')
        """
        页面接口示例：alipay.trade.page.pay
        """
        # 对照接口文档，构造请求对象
        model = AlipayTradePagePayModel()
        model.out_trade_no = order_id
        model.total_amount = order.total_money
        model.subject = "天天生鲜%s" % order_id
        # model.body = "支付宝测试"
        model.product_code = "FAST_INSTANT_TRADE_PAY"
        settle_detail_info = SettleDetailInfo()
        settle_detail_info.amount = order.total_money
        settle_detail_info.trans_in_type = "userId"
        settle_detail_info.trans_in = "2088102181299913"
        settle_detail_infos = list()
        settle_detail_infos.append(settle_detail_info)
        settle_info = SettleInfo()
        settle_info.settle_detail_infos = settle_detail_infos
        model.settle_info = settle_info
        request = AlipayTradePagePayRequest(biz_model=model)
        # 得到构造的请求，如果http_method是GET，则是一个带完成请求参数的url，如果http_method是POST，则是一段HTML表单片段
        cli = client()
        response = cli.page_execute(request, http_method="GET")
        return JsonResponse({'code': 200, 'url': response})


class CheckOrderView(View):

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'code': 201, 'errmsg': '用户未登录！'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'code': 202, 'errmsg': '未获取到有效订单号，请核对后再次提交！'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_status=0)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 203, 'errmsg': '未查询到该用户的有效订单，请核对后再次提交！'})

        cli = client()
        model = AlipayTradeQueryModel()
        model.out_trade_no = order_id
        request = AlipayTradeQueryRequest(biz_model=model)
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        for i in range(5):
            time.sleep(10)
            reponse = cli.execute(request)
            reponse = json.loads(reponse)
            if reponse['code'] == '10000' and reponse['trade_status'] == 'TRADE_SUCCESS':
                order.pay_status = 1
                order.save()
                return JsonResponse({'code': 200, 'msg': '支付成功！'})
            else:
                time.sleep(5)
                if i == 4:
                    return JsonResponse({'code': 204, 'errmsg': '支付失败，请重新发起支付！'})















