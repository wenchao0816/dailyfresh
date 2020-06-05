from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField

# Create your models here.
class GoodsSPU(BaseModel):
    name = models.CharField(max_length=50, verbose_name='商品SPU名称')
    details = HTMLField(blank=True, verbose_name='商品详情')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'df_goods_spu'
        verbose_name = '商品表'
        verbose_name_plural = verbose_name

class GoodsSKU(BaseModel):
    STATUS_CHOICES = ((1, '上架'), (0, '下架'))

    goods_name = models.CharField(max_length=20, verbose_name='商品名称')
    brief = models.CharField(max_length=50, verbose_name='简介')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    unit = models.CharField(max_length=10, verbose_name='单位')
    stock = models.FloatField(verbose_name='库存')
    sales_volume = models.IntegerField(default=0, verbose_name='销量')
    pictures = models.ImageField(upload_to='goods', verbose_name='图片')
    status = models.SmallIntegerField(default=1, choices=STATUS_CHOICES, verbose_name='商品状态')
    kinds = models.ForeignKey('GoodsKinds', verbose_name='商品种类', on_delete=models.CASCADE)
    SPU_id = models.ForeignKey('GoodsSPU', on_delete=models.CASCADE)

    def __str__(self):
        return self.goods_name

    class Meta:
        db_table = 'df_goods_sku'
        verbose_name = '商品配置表'
        verbose_name_plural = verbose_name

class GoodsKinds(BaseModel):
    name = models.CharField(max_length=20, verbose_name='商品种类')
    logo = models.CharField(max_length=10, verbose_name='商品logo')
    images = models.ImageField(upload_to='goods', verbose_name='商品图片')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'df_goods_kinds'
        verbose_name = '商品种类表'
        verbose_name_plural = verbose_name

class GoodsImages(BaseModel):
    images = models.ImageField(upload_to='goods', verbose_name='商品图片')
    goods_sku = models.ForeignKey('GoodsSKU', verbose_name='商品名称', on_delete=models.CASCADE)

    def __str__(self):
        return self.goods_sku.goods_name

    class Meta:
        db_table = 'df_goods_images'
        verbose_name = '商品图片表'
        verbose_name_plural = verbose_name

class GoodsIndexImages(BaseModel):
    images = models.ImageField(upload_to='goods', verbose_name='轮播图片')
    index = models.IntegerField(verbose_name='图片序号')
    sku = models.ForeignKey('GoodsSKU', on_delete=models.CASCADE, default=1, verbose_name='商品')

    def __str__(self):
        return self.sku.goods_name

    class Meta:
        db_table = 'df_goods_index_images'
        verbose_name = '轮播图片表'
        verbose_name_plural = verbose_name

class IndexTypeGoodsBanner(BaseModel):
    DISPLAY_TYPE_CHOICES = (
        (0, "标题"),
        (1, "图片")
    )

    kinds = models.ForeignKey('GoodsKinds', verbose_name='商品类型', on_delete=models.CASCADE)
    sku = models.ForeignKey('GoodsSKU', verbose_name='商品SKU', on_delete=models.CASCADE)
    display_type = models.SmallIntegerField(default=1, choices=DISPLAY_TYPE_CHOICES, verbose_name='展示类型')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    def __str__(self):
        return self.kinds.name

    class Meta:
        db_table = 'df_index_type_goods'
        verbose_name = "主页分类展示商品"
        verbose_name_plural = verbose_name


class GoodsActiveImages(BaseModel):
    active_name = models.CharField(max_length=50, verbose_name='活动名称')
    active_images = models.ImageField(upload_to='goods', verbose_name='活动图片')
    active_link = models.CharField(max_length=128, verbose_name='活动链接')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    def __str__(self):
        return self.active_name

    class Meta:
        db_table = 'df_goods_active_images'
        verbose_name = '商品活动图片'
        verbose_name_plural = verbose_name