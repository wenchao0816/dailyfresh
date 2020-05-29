from django.contrib import admin
from django.core.cache import cache
from apps.goods.models import GoodsImages
from apps.goods import models
from celery_tasks.tasks import generate_static_index_html

# Register your models here.

class BaseModelAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        generate_static_index_html.delay()
        cache.delete('index_cache_data')

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        generate_static_index_html.delay()
        cache.delete('index_cache_data')


class GoodsImagesAdmin(BaseModelAdmin):
    pass


class GoodsSKUAdmin(BaseModelAdmin):
    pass


class GoodsKindsAdmin(BaseModelAdmin):
    pass


class GoodsIndexImagesAdmin(BaseModelAdmin):
    pass


class GoodsActiveImagesAdmin(BaseModelAdmin):
    pass


admin.site.register(GoodsImages, GoodsImagesAdmin)
admin.site.register(models.GoodsKinds, GoodsKindsAdmin)
admin.site.register(models.GoodsSKU, GoodsSKUAdmin)
admin.site.register(models.GoodsSPU)
admin.site.register(models.GoodsActiveImages, GoodsActiveImagesAdmin)
admin.site.register(models.GoodsIndexImages, GoodsIndexImagesAdmin)
admin.site.register(models.IndexTypeGoodsBanner)
