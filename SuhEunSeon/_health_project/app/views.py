from django.shortcuts import render, redirect, resolve_url
# from .models import Question, Answer, QuestionForm
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def main_view(request):
    return render(request, 'app/main.html')

def select_view(request):
    return render(request, 'app/select.html')

def rag_recommend_view(request):
    return render(request, 'app/rag_recommend.html')

def ocr_llm_view(request):
    return render(request, 'app/ocr_llm.html')
