from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name = 'index'),

    path('rag_chatbot', views.rag_chatbot, name='rag_chatbot'), # rag_chatbot
    path('ocr_llm', views.ocr_llm, name='ocr_llm'), # ocr_llm
]