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
                auth.login(request, authenticated_user)

            return redirect('app:main')
    else:
        form = UserForm()

    return render(request, 'uauth/signup.html', {'form': form})


def check_usermail(request):
  """
  회원가입시 email 중복여부를 검사하는 ajax처리 뷰함수
  """
  useremail = request.GET.get('email')
  # email 사용가능 여부 
  available = User.objects.filter(useremail=useremail).exists() == False
  print(f"{useremail=}, {available=}")

  return JsonResponse({'available': available})