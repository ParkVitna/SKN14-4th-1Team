from django.shortcuts import render

# Create your views here.
def home(request):

    return render(request, 'app/home.html')

def search(request):
    # 검색 페이지
    q = request.GET.get("q", "")
    ctx = {"q": q}
    return render(request, "app/search.html", ctx)

def recommend(request):
    # 추천(챗봇) 페이지
    return render(request, "app/recommend.html")