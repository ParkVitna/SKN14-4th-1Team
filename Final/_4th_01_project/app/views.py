from django.shortcuts import render

def home(request):
    return render(request, 'app/home.html')

def main(request):
    return render(request, 'app/main.html')

def chat_recommand(request):
    return render(request, 'app/chat_recommand.html')

def photo_search(request):
    return render(request, 'app/photo_search.html')

