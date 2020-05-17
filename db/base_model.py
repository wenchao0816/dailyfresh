# coding=utf-8
from django.db import models

class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    isDel = models.BooleanField(default=False)