from django.shortcuts import render
from django.contrib import auth # 장고가 제공하는 로그아웃 처리
from django.shortcuts import redirect
from django.db import transaction
from .models import UserForm, UserDetail
from django.contrib.auth.models import User
from django.http import JsonResponse

# Create your views here.
# def signup(request):
#     return render(request, 'uauth/signup.html')

@transaction.atomic
def signup(request):
  if request.method == 'POST':
    form = UserForm(request.POST, request.FILES)
    print(f'[DEBUG] POST data: {request.POST}')

    if form.is_valid():
       print(f'{form.cleaned_data=}')
       # User 모델 저장
       user = form.save(commit=True)
       print(f'{user=}')

       # UserDetail 모델 저장
       userdetail = UserDetail(
            user=user,
            birthday=form.cleaned_data.get('birthday'),
            gender=form.cleaned_data.get('gender'),
            is_pregnant=form.cleaned_data.get('is_pregnant', False),
            health_interests=form.cleaned_data.get('health_interests', [])
        )

       userdetail.save()
    #    print(f'저장: {userdetail=}')
       print(f'[DEBUG] UserDetail created: {userdetail} (id={userdetail.id})')

       # 회원가입 동시에 로그인처리
    #    username = form.cleaned_data['username']
    #    password = form.cleaned_data['password1']
    #    authenticated_user = auth.authenticate(username=username, password=password) # 인증
    #    if authenticated_user is not None:
    #       auth.login(request, authenticated_user) # 로그인처리
       return redirect('uauth:login')
  else: 
    form = UserForm()

  return render(request, 'uauth/signup.html', {'form': form})