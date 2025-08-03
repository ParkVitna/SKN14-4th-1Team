from django.shortcuts import render
from .config import load_config
from .rag_chatbot import RAG_Chatbot

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

    if request.method == "POST":
        img_file = request.FILES.get("image")

    if q or img_file:
        try:
            response_text = rag.run(
                question=q,
                use_ocr=bool(img_file),
                img_file=img_file
            )
        except Exception as e:
            response_text = f"에러 발생: {str(e)}"

    ctx = {
        "q": q,
        "response": response_text
    }
    return render(request, "app/search.html", ctx)


def recommend(request):
    # 추천(챗봇) 페이지
    return render(request, "app/recommend.html")