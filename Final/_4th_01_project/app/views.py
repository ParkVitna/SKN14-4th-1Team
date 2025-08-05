import re
from django.shortcuts import render
from .config import load_config
from .rag_chatbot import RAG_Chatbot
from django.core.files.storage import FileSystemStorage
from .utils import parse_product_detail

def home(request):
    return render(request, 'app/home.html')

def main(request):
    return render(request, 'app/main.html')

def chat_recommand(request):
    return render(request, 'app/chat_recommand.html')

def search(request):
    response_text = ""
    q = ""
    img_file = None
    image_url = None

    if request.method == "POST":
        q = request.POST.get("q", "").strip()
        img_file = request.FILES.get("image")
        
        if img_file:
            fs = FileSystemStorage()
            filename = fs.save(img_file.name, img_file)
            image_url = fs.url(filename)

        if q or img_file:
            try:
                # ✅ search에서는 무조건 제품 기반 검색으로 고정
                response_text = rag.run(
                    question=q,
                    use_ocr=bool(img_file),
                    img_file=img_file,
                    search_mode=True  # 고정!
                )
            except Exception as e:
                response_text = f"에러 발생: {str(e)}"

    print("🔍 response_text:", response_text)

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

