import re
from django.shortcuts import render
from .config import load_config
from .rag_chatbot import RAG_Chatbot
from django.core.files.storage import FileSystemStorage

cfg = load_config()
rag = RAG_Chatbot(cfg)

# Create your views here.
def home(request):

    return render(request, 'app/home.html')

# def search(request):
#     # 검색 페이지
#     q = request.GET.get("q", "")
#     ctx = {"q": q}
#     return render(request, "app/search.html", ctx)

def search(request):
    response_text = ""
    q = request.GET.get("q", "")
    img_file = None

    if request.method == "POST" and request.FILES.get('image'):
        img_file = request.FILES.get("image")
        fs = FileSystemStorage()
        filename = fs.save(img_file.name, img_file)
        image_url = fs.url(filename)

    if q or img_file:
        try:
            print('q', q)
            response_text = rag.run(
                question=q,
                use_ocr=bool(img_file),
                img_file=img_file
            )
        except Exception as e:
            response_text = f"에러 발생: {str(e)}"
    product_list = []
    if response_text:
        # 제품명 기준으로 분리: <<제품명>>, <<제품명2>>, ...
        pattern = r"<<(.+?)>>\s*- 브랜드:.*?(?=(<<|$))"  # lookahead로 다음 제품 또는 끝까지
        matches = re.finditer(pattern, response_text, re.DOTALL)

        
        for match in matches:
            title = match.group(1).strip()
            detail = match.group(0).strip()
            product_list.append({
                "name": title,
                "detail": detail
            })
        ctx = {"response_list": product_list,
           "image_url": image_url}

        return render(request, "app/search.html", ctx)

    return render(request, "app/search.html", {"response_list": product_list})

    # ctx = {
    #     "q": q,
    #     "response": response_text
    # }
    # return render(request, "app/search.html", ctx)


def recommend(request):
    # 추천(챗봇) 페이지
    return render(request, "app/recommend.html")