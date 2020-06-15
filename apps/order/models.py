from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField

# Create your models here.

class OrderInfo(BaseModel):
    PAY_CHOICES = (
        ('0', '货到付款'),
        ('1', '支付宝'),
        ('2', '微信'),
        ('3', '银行卡')
    )

    PAY_STATUS = (
        ('0', '待支付'),
        ('1', '支付成功'),
        ('2', '待收货'),
        ('3', '订单完成'),
    )

    order_id = models.CharField(max_length=255, primary_key=True, null=False, verbose_name='订单ID')
    address = models.ForeignKey('user.Address', null=False, verbose_name='发货地址', on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', null=False, verbose_name='用户ID', on_delete=models.CASCADE)
    pay_ways = models.SmallIntegerField(choices=PAY_CHOICES, null=False, verbose_name='支付方式')
    amount = models.IntegerField(verbose_name='总数量')
    total_money = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name='总金额')
    freight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='运费')
    pay_status = models.SmallIntegerField(choices=PAY_STATUS, verbose_name='支付状态')

    class Meta:
        db_table = 'df_order_info'
        verbose_name = '订单信息表'
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):
    order = models.ForeignKey('OrderInfo', on_delete=models.CASCADE)
    SKU = models.ForeignKey('goods.GoodsSKU', on_delete=models.CASCADE)
    goods_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name='商品数量')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
    comment = HTMLField()

    class Meta:
        db_table = 'df_order_goods'
        verbose_name = '订单商品表'
        verbose_name_plural = verbose_name