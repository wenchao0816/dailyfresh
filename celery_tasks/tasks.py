# coding=utf-8
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader
from apps.goods import models

app = Celery('celery_tasks', broker='redis://192.168.44.128:6379/0')

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

def generate_static_index_html():
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
    temp = loader.get_template('static/static_index.html')
    static_index_html = temp.render(content)
    save_path = os.path.join(settings.BASE_DIR, 'static/static_index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
