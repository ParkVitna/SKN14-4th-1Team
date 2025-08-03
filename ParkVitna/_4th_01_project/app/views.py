from django.shortcuts import render

def index(request):
    return render(request, 'app/main.html')

def chat_recommand(request):
    return render(request, 'app/chat_recommand.html')

def photo_search(request):
    return render(request, 'app/photo_search.html')

