from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class UserDetail(models.Model):
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]

    HEALTH_CHOICES = [
        ('immune', '면역력 강화'),
        ('skin', '피부 건강'),
        ('energy', '에너지/피로 회복'),
        ('joint', '관절 건강'),
        ('digest', '소화/장 건강'),
        ('stress', '스트레스 관리'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    is_pregnant = models.BooleanField(default=False)
    health_interests = models.JSONField(default=list)

    def __str__(self):
        return self.user.username
    


class UserForm(UserCreationForm): # 사용자 회원가입 폼(입력)
    birthday = forms.DateField(label="Birthday", required=False)

    gender = forms.ChoiceField(
        label="gender", 
        choices=UserDetail.GENDER_CHOICES,
        widget=forms.Select(attrs={'onchange': 'togglePregnantCheckbox()', 'class': 'form-select'}) # onchange 이벤트 추가
    )

    is_pregnant = forms.BooleanField(
        label="is_pregnant",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    health_interests = forms.MultipleChoiceField(
        label="health_interests",
        choices=UserDetail.HEALTH_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email")