from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

from app import views as app_views

app_name = 'uauth'

urlpatterns = [
    # path(url, view_function, name)
    path('login/', auth_views.LoginView.as_view(template_name='uauth/login.html'), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    # 추가
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/edit/', views.mypage_edit, name='mypage_edit'),

    
    path('', app_views.main, name='main'),  # 로그인 후 이동할 메인 페이지
]