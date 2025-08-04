from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # path(url, view_function, name)
    path('', views.index, name='index'),
    path('chat', views.chat_recommand, name='chat_recommand'),
    path('photo', views.photo_search, name='photo_search'),
]