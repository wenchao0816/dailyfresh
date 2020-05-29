from django.shortcuts import render
from django.views.generic import View
from django.core.cache import cache
from apps.goods import models
from django_redis import get_redis_connection

# Create your views here.

class IndexView(View):

    def get(self, request):
        if cache.get('index_cache_data') is None:
            kinds = models.GoodsKinds.objects.all()
            goods_index_images = models.GoodsIndexImages.objects.all().order_by('index')
            goods_active_images = models.GoodsActiveImages.objects.all().order_by('-id')[:2]
            for kind in kinds:
                image_banner = models.IndexTypeGoodsBanner.objects.filter(kinds=kind, display_type=1).order_by('index')
                title_banner = models.IndexTypeGoodsBanner.objects.filter(kinds=kind, display_type=0).order_by('index')
                kind.image_banner = image_banner
                kind.title_banner = title_banner
            content = {
                'kinds': kinds,
                'goods_index_images': goods_index_images,
                'goods_active_images': goods_active_images,
            }
            cache.set('index_cache_data', content, 3600)
        else:
            content = cache.get('index_cache_data')
        cart_count = 0
        # if 'cart_count' in request.COOKIES:
        #     cart_count = request.COOKIES['cart_count']
        # 判断是否登录，确认登陆后获取购物车的数据
        user = request.user
        if user.is_authenticated:
            cart_key = 'cart_key_%d' % user.id
            conn = get_redis_connection('default')
            cart_count = conn.hlen(cart_key)
        content['cart_count'] = cart_count
        return render(request, 'goods/index.html', content)
