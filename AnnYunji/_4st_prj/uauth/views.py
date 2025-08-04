from django.shortcuts import render
from django.contrib import auth # 장고가 제공하는 로그아웃 처리
from django.shortcuts import redirect
from django.db import transaction
# from .models import UserForm, UserDetail
from django.contrib.auth.models import User
from django.http import JsonResponse

def signup(request):
    return render(request, 'uauth/signup.html')