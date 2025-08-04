from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

# 사용자 상세정보를 저장할 모델
class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    is_pregnancy = models.BooleanField(default=False)
    health_concerns = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

# 회원가입 시 사용할 폼
class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birthday = forms.DateField(label="Birthday", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    sex = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], required=False)
    is_pregnancy = forms.BooleanField(required=False)
    health_concerns = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
