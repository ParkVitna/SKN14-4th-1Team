from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'main/index.html')

def chat(request):
    return render(request, 'main/chat.html')

def ocr(request):
    return render(request, 'main/ocr.html')

def signup(request):
    return render(request, 'main/signup.html')

def profile(request):
    return render(request, 'main/profile.html')