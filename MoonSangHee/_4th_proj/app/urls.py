from django.urls import path, include
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home, name='home'),
    path("search/", views.search, name="search"),
    path("recommend/", views.recommend, name="recommend"),
    # path('app/', include('app.urls')), # /app/으로 시작하는 요청을 app/urls.py로 위임
    # # path('', RedirectView.as_view(url='/app/')), # /루트 주소/로 접속하면 자동으로 /app/으로
    # path('uauth/', include('uauth.urls')), 
]
