from django.shortcuts import render
from .config import load_config
from .rag_chatbot import RAG_Chatbot
from django.views.decorators.csrf import csrf_exempt
from .image_search import search_image_google  # 이미지 검색 함수 위치에 따라 조정
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
        print("DEBUG: items from rag.run =", items)

        # 2) 이미지 URL이 없거나 빈 문자열인 경우 Google 이미지 검색으로 보완
        for item in items:
            if not item.get('image_url'):  # None 또는 빈 문자열 모두 포함
                name = item.get('name', '')
                brand = item.get('brand', '')
                image_url = search_image_google(name, brand)
                item['image_url'] = image_url if image_url else None
        
        print("DEBUG: items after image search =", items)

        # 3) JSON 응답 반환 (AJAX용)
        return JsonResponse({'items': items}, json_dumps_params={'ensure_ascii': False})
    else:
        return HttpResponseBadRequest('POST 요청만 허용됩니다.')