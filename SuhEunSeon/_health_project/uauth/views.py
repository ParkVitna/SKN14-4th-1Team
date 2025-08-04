from django.shortcuts import render
from django.contrib import auth
from django.shortcuts import redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.http import JsonResponse

# 로그아웃 처리
def logout(request):
    auth_logout(request)
    return redirect('uauth:login')

# 회원가입 페이지 렌더링
def signup(request):
    if request.method == 'POST':
        # 아직 회원가입 코드 아직은 없음
        return redirect('uauth:login')
    return render(request, 'uauth/signup.html')

# 아이디 중복 체크 (비동기 예시 - 지금은 항상 가능하다고 응답)
def check_username(request):
    return JsonResponse({'available': True})