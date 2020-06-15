from django.urls import path
from apps.user import views

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('active/<str:token>', views.ActiveView.as_view(), name='active'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('order/<int:page>', views.UserCenterOrder.as_view(), name='order'),
    path('user_center_site', views.UserCenterSite.as_view(), name='site'),
    path('', views.UserCenterInfo.as_view(), name='user')
    # path('registration', views.registration),
]
