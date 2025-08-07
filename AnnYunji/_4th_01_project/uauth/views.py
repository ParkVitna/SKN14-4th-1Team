from django.shortcuts import render, redirect
from django.contrib import auth
from django.db import transaction

from .models import UserForm, UserDetail


# 추가
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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


#=====추가


# 마이페이지
@login_required
def mypage(request):
    return render(request, 'uauth/mypage.html', {'user': request.user})

# 마이페이지 수정
@login_required
def mypage_edit(request):
    print("🟢🟢🟢🟢🟢🟢🟢🟢 mypage_edit ")
    user = request.user
    detail, created = UserDetail.objects.get_or_create(user=user)
    print("🟢🟢🟢현재 로그인한 사용자:", user)

    if request.method == 'POST':
        email = request.POST.get('email')
        birthday = request.POST.get('birthday')
        gender = request.POST.get('gender')
        is_pregnant = request.POST.get('is_pregnant') == 'on'  # checkbox는 'on'일 때 체크됨
        health_concerns = request.POST.getlist('health_concerns')

        print(f"🟢🟢🟢폼에서 받은 값: - email: {email}, birthday: {birthday}, gender: {gender}, pregnant: {is_pregnant}, concerns: {health_concerns}")

        if email:
            user.email = email
            user.save()

        if birthday:
            detail.birthday = birthday

        if gender:
            detail.gender = gender

        detail.is_pregnant = is_pregnant

        if health_concerns:
            detail.health_concerns = ", ".join(health_concerns)

        detail.save()

        return redirect('uauth:mypage')

    return render(request, 'uauth/mypage_edit.html', {'user': user})