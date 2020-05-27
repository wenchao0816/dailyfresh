from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django_redis import get_redis_connection

from apps.user.models import User, Address
from apps.order.models import OrderInfo
from apps.goods.models import GoodsSKU
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from utils.mixin import LoginRequiredMixin
from celery_tasks.tasks import send_register_active_email
import re

# Create your views here.

class RegisterView(View):

    def get(self, request):
        return render(request, 'goods/register.html')

    def post(self, request):
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, cpassword, email, allow]):
            msg = '参数数据不完整，请重新输入！'
            return render(request, 'goods/register.html', {'errmsg':msg})
        if password != cpassword:
            msg = '两次密码输入不一致，请重新输入！'
            return render(request, 'goods/register.html', {'errmsg': msg})
        if not re.match(r'^[a-z0-9][\w.-]*@[a-z0-9-]+(.[a-z]{2,5}){1,2}$', email):
            msg = '邮箱输入不符合规则，请重新输入！'
            return render(request, 'goods/register.html', {'errmsg': msg})
        try:
            User.objects.get(username=username)
            msg = '用户名已注册，请重新输入！'
            return render(request, 'goods/register.html', {'errmsg': msg})
        # 进行业务处理
        except:
            user = User.objects.create_user(username, email, password)
            user.is_active = 0
            user.save()
        # 加密拼接激活url
        ser = Serializer(settings.SECRET_KEY, expires_in=300)
        obj = {'confirm': user.id}
        res = ser.dumps(obj).decode()
        # # 发送邮件
        # subject = '欢迎您！'
        # message = ''
        # sender = settings.EMAIL_HOST_USER
        # email = [email]
        # html_msg = '<h1>%s欢迎您！<h1>' \
        #            '<br><p>点击下面链接进行账户激活：<p>' \
        #            '<br>' \
        #            '<a href=\'http://127.0.0.1:8000/user/active/%s\'>' \
        #            'http://127.0.0.1:8000/user/active/%s<a>' % (username, res, res)
        # send_mail(subject, message, sender, email, html_message=html_msg)

        send_register_active_email.delay(email, username, res)

        # 返回应答
        return redirect(reverse('goods:index'))

class ActiveView(View):
    # 验证用户信息并激活
    def get(self, request, token):
        ser = Serializer(settings.SECRET_KEY, expires_in=300)
        try:
            res = ser.loads(token)
            user = User.objects.get(id=res['confirm'])
            user.is_active = 1
            user.save()
            return redirect(reverse('goods:index'))
        except:
            pass

class LoginView(View):
    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES['username']
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'user/login.html', {'username':username, 'checked':checked})

    def post(self, request):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        if not all([username, pwd]):
            return render(request, 'goods/index.html', {'errmsg': '请输入用户名或密码！'})
        user = authenticate(username=username, password=pwd)
        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)
                rem = request.POST.get('remember')
                if rem:
                    response.set_cookie('username', username, max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'user/login.html', {'errmsg': '该用户尚未激活！'})
        else:
            return render(request, 'user/login.html', {'errmsg': '用户名或密码输入错误！'})


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect(reverse('goods:index'))


class UserCenterInfo(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        address = Address.objects.get_default_address(user)
        con = get_redis_connection('default')
        history_key = 'history%d' % user.id
        history_val = con.lrange(history_key, 0, 4)
        goods_li = [GoodsSKU.objects.get(id=index) for index in history_val]
        return render(request, 'user/user_center_info.html', {'page': 'user', 'address': address, 'goods_li': goods_li})

class UserCenterOrder(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        orders = OrderInfo.objects.filter(user=user)
        return render(request, 'user/user_center_order.html', {'page': 'order', 'orders': orders})


class UserCenterSite(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        # try:
        #     address = Address.objects.filter(user=user)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        return render(request, 'user/user_center_site.html', {'page': 'site', 'address': address})

    def post(self, request):
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        if not all([receiver, addr, phone]):
            return render(request, 'user/user_center_site.html', {'errmsg':'输入信息不完整！'})
        if not re.match(r'^1[346789][0-9]{9}$', phone):
            return render(request, 'user/user_center_site.html', {'errmsg':'联系电话输入不正确！'})
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)
        if address:
            isDef = False
        else:
            isDef = True
        Address.objects.create(receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=isDef,
                               user=user)
        return redirect(reverse('user:site'))
