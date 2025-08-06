from django.shortcuts import render
from .config import load_config
from .rag_chatbot import RAG_Chatbot
###
import json
from django.http import JsonResponse

cfg = load_config()
rag = RAG_Chatbot(cfg)

def home(request):
    return render(request, 'app/home.html')

def main(request):
    return render(request, 'app/main.html')

def chat_recommand(request):
    return render(request, 'app/chat_recommand.html')

def photo_search(request):
    return render(request, 'app/photo_search.html')


##### 수정
def chatbot_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')
        use_ocr = data.get('use_ocr', False)

        cfg = load_config()
        chatbot = RAG_Chatbot(cfg)
        response = chatbot.run(question=question, use_ocr=use_ocr)

        # JSON 응답 반환 (AJAX용)
        return JsonResponse({"response": response})
    else:
        # GET 요청 처리 (기본 페이지 렌더링)
        return render(request, 'app/chatbot_view.html')