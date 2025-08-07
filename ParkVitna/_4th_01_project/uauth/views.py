from django.shortcuts import render, redirect
from django.contrib import auth
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import UserForm, UserDetail

import logging
logger = logging.getLogger(__name__)

def logout(request):
    auth.logout(request)
    return redirect('app:home')


@transaction.atomic
def signup(request):
    signup_failed = False  # 실패 여부 플래그

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()

            # 건강 관심사 체크박스 값 가져오기
            health_concerns = ", ".join(request.POST.getlist('health_concerns'))

            # 임신 여부 체크박스 값 처리
            is_pregnant = 'is_pregnant' in request.POST

            user_detail = UserDetail.objects.create(
                user=user,
                birthday=form.cleaned_data.get('birthday'),
                gender=form.cleaned_data.get('gender'),
                is_pregnant=is_pregnant,
                health_concerns=health_concerns
            )

            # 로그인 처리
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            authenticated_user = auth.authenticate(username=username, password=password)

            if authenticated_user is not None:
                print("회원가입 성공 진입")
                auth.login(request, authenticated_user)
                return redirect('app:main')  # 여기가 로그인 후 리디렉션되는 URL 네임스페이스

            # 로그인 실패 시 (거의 발생하지 않지만 대비)
            signup_failed = True

        else:
            signup_failed = True  # 유효성 검증 실패 시 True

    else:
        form = UserForm()

    return render(request, 'uauth/signup.html', {'form': form, 'signup_failed': signup_failed})




def check_username(request):
    """
    회원가입시 username 중복여부를 검사하는 ajax처리 뷰함수
    """
    username = request.GET.get('username')
    # username 사용가능 여부 
    available = User.objects.filter(username=username).exists() == False

    return JsonResponse({'available': available})