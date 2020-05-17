from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
class User(AbstractBaseUser, BaseModel):
    identifier = models.CharField(max_length=40, unique=True)
    USERNAME_FIELD = 'identifier'

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户信息表'
        verbose_name_plural = verbose_name

class Address(BaseModel):
    addressee = models.CharField(max_length=20, verbose_name='收件人')
    address = models.CharField(max_length=50, verbose_name='收件地址')
    postcode = models.IntegerField(verbose_name='邮编')
    phone_num = models.IntegerField(verbose_name='联系方式')
    user_id = models.IntegerField(verbose_name='用户ID')
    isDef = models.BooleanField(default=True,verbose_name='是否默认')

    class Meta:
        db_table = 'df_user_address'
        verbose_name = '用户地址表'
        verbose_name_plural = verbose_name