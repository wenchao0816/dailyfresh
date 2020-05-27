# coding=utf-8
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()


app = Celery('celery_tasks', broker='redis://localhost:6379/1')

@app.task
def send_register_active_email(to_email, username, token):
    # 发送邮件
    subject = '欢迎您！'
    message = ''
    sender = settings.EMAIL_HOST_USER
    email = [to_email]
    html_msg = '<h1>%s欢迎您！<h1>' \
               '<br><p>点击下面链接进行账户激活：<p>' \
               '<br>' \
               '<a href=\'http://127.0.0.1:8000/user/active/%s\'>' \
               'http://127.0.0.1:8000/user/active/%s<a>' % (username, token, token)
    send_mail(subject, message, sender, email, html_message=html_msg)