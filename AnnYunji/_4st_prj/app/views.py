from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'app/main.html')


def rag_chatbot(request):
    return render(request, 'app/rag_chatbot.html')


def ocr_llm(request):
    return render(request, 'app/ocr_llm.html')