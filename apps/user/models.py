from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser, BaseModel):

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户信息表'
        verbose_name_plural = verbose_name


class AddressManage(models.Manager):

    def get_default_address(self, user):
        try:
            address = Address.objects.get(user=user, is_default=1)
        except Address.DoesNotExist:
            address = None
        return address


class Address(BaseModel):
    user = models.ForeignKey('User', verbose_name='所属账户', on_delete=models.CASCADE)
    receiver = models.CharField(max_length=20, verbose_name='收件人')
    addr = models.CharField(max_length=256, verbose_name='收件地址')
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')
    phone = models.CharField(max_length=11, verbose_name='联系电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认')

    objects = AddressManage()

    class Meta:
        db_table = 'df_user_address'
        verbose_name = '用户地址表'
        verbose_name_plural = verbose_name