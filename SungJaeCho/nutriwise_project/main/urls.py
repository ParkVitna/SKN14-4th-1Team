from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('ocr/', views.ocr, name='ocr'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
]