import re, json
from django.http import JsonResponse
from django.shortcuts import render
from .rag_chatbot import RAG_Chatbot
from django.core.files.storage import FileSystemStorage
from .utils import parse_product_detail
from django.contrib.auth.decorators import login_required
from app.models import ChatMessage

rag = RAG_Chatbot()

def home(request):
    return render(request, 'app/home.html')

def main(request):
    return render(request, 'app/main.html')

@login_required
def chat_recommand(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')
        user = request.user

        # 반드시 상담 시작을 먼저 해야 함
        if not request.session.get('is_chatting', False) and question != "상담 시작":
            return JsonResponse({'response': '먼저 "상담 시작"을 입력해야 상담을 진행할 수 있습니다.'})

        if question == "상담 시작":
            session_id = request.session.session_key
            ChatMessage.objects.filter(session_id=session_id).delete()
            request.session['is_chatting'] = True
            return JsonResponse({'response': '상담이 새로 시작되었습니다! 무엇이 궁금하신가요?'})

        if question == "상담 종료":
            session_id = request.session.session_key
            ChatMessage.objects.filter(session_id=session_id).delete()
            request.session['is_chatting'] = False
            return JsonResponse({'response': '상담이 종료되었습니다. 상담 내역이 모두 삭제되었습니다.'})
        
        # 3. 기본 채팅 처리
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        ChatMessage.objects.create(session_id=session_id, message_type='human', content=question)

        chat_history = []
        if session_id:
            chat_history = [
                {'role': msg.message_type if msg.message_type in ['human', 'ai'] else 'ai', 'content': msg.content}
                for msg in ChatMessage.objects.filter(session_id=session_id).order_by('created_at')
            ]

        response = rag.run(question=question, user=user, chat_history=chat_history)

        ChatMessage.objects.create(session_id=session_id, message_type='ai', content=response)

        return JsonResponse({'response': response})

    else:
        return render(request, 'app/chat_recommand.html')


def search(request):
    response_text = ""
    q = ""
    img_file = None
    image_url = None
    product_list = None

    if request.method == "POST":
        q = request.POST.get("q", "").strip()
        img_file = request.FILES.get("image")

        if img_file:
            fs = FileSystemStorage()
            filename = fs.save(img_file.name, img_file)
            image_url = fs.url(filename)

        if q or img_file:
            try:
                response_text = rag.run(question=q, use_ocr=bool(img_file), img_file=img_file, search_mode=True)
            except Exception as e:
                response_text = f"에러 발생: {str(e)}"

        # print("🔍 response_text:", response_text)

        product_list = []

        if response_text:
            pattern = r"<<.+?>>.*?(?=(<<|$))"
            matches = re.finditer(pattern, response_text, re.DOTALL)

            for match in matches:
                raw_block = match.group(0).strip()
                parsed = parse_product_detail(raw_block)
                product_list.append(parsed)

    ctx = {
        "response_list": product_list,  
        "image_url": image_url,
        "q": q
    }

    return render(request, "app/search.html", ctx)




