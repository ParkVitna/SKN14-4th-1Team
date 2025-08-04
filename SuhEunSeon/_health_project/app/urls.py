from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main'),  # 메인 페이지
    path('select/', views.select_view, name='select'),  # 기능 선택 페이지
    path('rag_recommend/', views.rag_recommend_view, name='rag_recommend'),  # RAG 추천
    path('ocr_llm/', views.ocr_llm_view, name='ocr_llm'),  # OCR 업로드
]
