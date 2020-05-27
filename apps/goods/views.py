from django.shortcuts import render
from django.views.generic import View
from apps.goods import models

# Create your views here.

class IndexView(View):

    def get(self, request):
        kinds = models.GoodsKinds.objects.all()
        goods_index_images = models.GoodsIndexImages.objects.all().order_by('index')
        goods_active_images = models.GoodsActiveImages.objects.all().order_by('-id')[:2]
        goods_spu = models.GoodsSPU.objects.all()[0:3]
        content = {
            'kinds': kinds,
            'goods_index_images': goods_index_images,
            'goods_active_images': goods_active_images,
            'goods_spu': goods_spu
        }
        return render(request, 'goods/index.html', content)
