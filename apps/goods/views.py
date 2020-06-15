from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from django.core.cache import cache
from django.core.paginator import Paginator
from apps.goods.models import GoodsKinds, GoodsIndexImages, GoodsActiveImages, IndexTypeGoodsBanner, GoodsSKU
from utils.redis_connect import HashRedisConnect, get_redis_connection
# Create your views here.


class IndexView(View):

    def get(self, request):
        if cache.get('index_cache_data') is None:
            kinds = GoodsKinds.objects.all()
            goods_index_images = GoodsIndexImages.objects.all().order_by('index')
            goods_active_images = GoodsActiveImages.objects.all().order_by('-id')[:2]
            for kind in kinds:
                image_banner = IndexTypeGoodsBanner.objects.filter(kinds=kind, display_type=1).order_by('index')
                title_banner = IndexTypeGoodsBanner.objects.filter(kinds=kind, display_type=0).order_by('index')
                kind.image_banner = image_banner
                kind.title_banner = title_banner
            context = {
                'kinds': kinds,
                'goods_index_images': goods_index_images,
                'goods_active_images': goods_active_images,
            }
            cache.set('index_cache_data', context, 3600)
        else:
            context = cache.get('index_cache_data')
        # 判断是否登录，确认登陆后获取购物车的数据
        cart = HashRedisConnect(request.user).get_all_cart() if request.user.is_authenticated else ''
        context['cart_num'] = len(cart)
        return render(request, 'goods/index.html', context)


class DetailsView(View):

    def get(self, request, gid):
        try:
            goods = GoodsSKU.objects.get(id=gid)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))
        kinds = GoodsKinds.objects.all()
        other_goods = GoodsSKU.objects.filter(kinds=goods.kinds).order_by('sales_volume')[:2]
        cart = HashRedisConnect(request.user).get_all_cart() if request.user.is_authenticated else ''
        goods_else = GoodsSKU.objects.filter(SPU_id=goods.SPU_id).exclude(id=gid)
        context = {
            'goods': goods, 
            'other_goods': other_goods,
            'kinds': kinds,
            'cart_num': len(cart),
            'goods_else': goods_else
            }

        if request.user.is_authenticated:
            history_key = 'history_%d' % request.user.id
            conn = get_redis_connection('history')
            conn.lrem(history_key, 0, gid)
            conn.lpush(history_key, gid)
            conn.ltrim(history_key, 0, 4)
        return render(request, 'goods/detail.html', context)


class GoodsListView(View):
    def get(self, request, kid, page):
        sort = request.GET.get('sort')
        if sort not in ['id', 'price', 'sales_volume']:
            sort = 'id'
        try:
            kinds = GoodsKinds.objects.get(id=kid)
        except GoodsKinds.DoesNotExist:
            return redirect(reverse('goods:index'))
        kinds_all = GoodsKinds.objects.all()
        goods = kinds.goodssku_set.all().order_by(sort)
        new_goods = goods.order_by('-create_time')[:2]
        cart = HashRedisConnect(request.user).get_all_cart() if request.user.is_authenticated else ''
        paginator = Paginator(goods, 1)
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        sku_pages = paginator.page(page)
        # TODO 进行页码控制
        if paginator.num_pages < 5:
            pages = range(1, paginator.num_pages+1)
        elif page <= 3:
            pages = range(1, 6)
        elif page >= paginator.num_pages-3:
            pages = range(paginator.num_pages-4, paginator.num_pages+1)
        else:
            pages = range(page-2, page+3)

        context = {
            'goods': goods,
            'kinds': kinds_all,
            'type': kinds,
            'new_goods': new_goods,
            'cart_num': len(cart),
            'sku_pages': sku_pages,
            'page': page,
            'sort': sort,
            'pages': pages
        }
        return render(request, 'goods/list.html', context)
