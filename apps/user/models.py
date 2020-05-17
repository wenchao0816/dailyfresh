from django.db import models
from db.base_model import BaseModel
# Create your models here.
class User():
    pass

class Address(BaseModel):
    addressee = models.CharField(max_length=20, verbose_name='收件人')
    address = models.CharField(max_length=50, verbose_name='收件地址')
    postcode = models.IntegerField(max_length=6, verbose_name='邮编')
    phone_num = models.IntegerField(max_length=11, verbose_name='联系方式')
    user_id = models.IntegerField(verbose_name='用户ID')
    isDef = models.BooleanField(default=True,verbose_name='是否默认')