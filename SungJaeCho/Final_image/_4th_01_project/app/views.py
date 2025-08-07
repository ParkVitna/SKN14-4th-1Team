from django.shortcuts import render
from .config import load_config
from .rag_chatbot import RAG_Chatbot
from django.views.decorators.csrf import csrf_exempt
###
import json
from django.http import JsonResponse, HttpResponseBadRequest

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
@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')
        use_ocr = data.get('use_ocr', False)

        
        # 1) RAG 챗봇 실행 → list[dict]
        items = rag.run(question=question, use_ocr=use_ocr)
        print("DEBUG: items from rag.run =", items)  # 이 로그로 실제 값 확인
        # JSON 응답 반환 (AJAX용)
        return JsonResponse({'items': items}, json_dumps_params={'ensure_ascii': False})
    else:
        # GET 요청 처리 (기본 페이지 렌더링)
        return HttpResponseBadRequest('POST 요청만 허용됩니다.')