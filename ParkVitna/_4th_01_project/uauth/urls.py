from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'uauth'

urlpatterns = [
    # path(url, view_function, name)
    path('login/', auth_views.LoginView.as_view(template_name='uauth/login.html'), name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('check_username/', views.check_username, name='check_username'),
]