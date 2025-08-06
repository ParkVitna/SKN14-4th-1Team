from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # path(url, view_function, name)
    path('', views.home, name='home'),
    path('main', views.main, name='main'),
    path('chat', views.chat_recommand, name='chat_recommand'),
    path('photo', views.photo_search, name='photo_search'),
    path('chatbot/', views.chatbot_view, name='chatbot_view'),
]