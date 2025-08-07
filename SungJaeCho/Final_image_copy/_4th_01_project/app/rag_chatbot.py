import os
import re
import json
from typing import Any, Dict, List, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .ocr_llm import OCR_LLM
from langchain.vectorstores import FAISS
from .image_search import search_image_google

FAISS_INDEX_PATH = "faiss_index"
RETRIEVER_K = 3

class RAG_Chatbot:
    def __init__(self, cfg: Dict[str, Any]):
        self.openai_api_key = os.getenv('OPENAI_API_KEY') # OpenAI API 키
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY') # Pinecone API 키 (사용 여부는 코드에 없음)
        self.cfg = cfg # 설정 딕셔너리
        self.ocr = OCR_LLM(cfg) # OCR 처리 객체
        self.openai_embedding_model = cfg["OPENAI_EMBEDDING_MODEL"] # 임베딩 모델 이름
        self.openai_model_name = cfg['OPENAI_MODEL_NAME'] # LLM 모델 이름
        self.embeddings = OpenAIEmbeddings(   # OpenAIEmbeddings 객체
            openai_api_key=self.openai_api_key,
            model=self.openai_embedding_model
        )
        self.vector_store = FAISS.load_local(  # FAISS 벡터 DB 로드
            FAISS_INDEX_PATH,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )
        self.retriever = self.vector_store.as_retriever(   # 벡터 DB 기반 유사도 검색 객체
            search_type='similarity',
            search_kwargs={'k': RETRIEVER_K}
        )

    def run(
        self,
        question: str = "", # 사용자 질문(문자열)
        use_ocr: bool = False, # OCR 사용여부
        img_file: Optional[Any] = None, # OCR 대상 이미지
        temperature: float = 0.3,
        max_token: int = 4096
    ) -> List[Dict[str, Any]]:
        if not question.strip():
            raise ValueError("질문이 비어 있습니다. 텍스트를 입력해 주세요.")

        llm = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            temperature=temperature,
            model_name=self.openai_model_name,
            max_tokens=max_token
        )

        try:
            retrieved_docs = self.retriever.invoke(question) # 호출해서 FAISS에서 유사 문서 3개 검색
            context = "\n---\n".join(doc.page_content for doc in retrieved_docs) # 	검색 결과를 줄바꿈 \n---\n으로 이어붙여 문맥 생성
            prompt_template = self.prompt(question=question, context=context) 
            response = llm.invoke(prompt_template) # LLM 호출 (llm.invoke(prompt_template))으로 답변 생성
            text = response.content.strip()
            if not text:
                raise RuntimeError("LLM 응답이 비어 있습니다.")
        except Exception as e:
            raise RuntimeError(f"텍스트 처리 중 오류가 발생했습니다: {e}")

        try:
            # LLM 응답에서 JSON 배열만 추출(정규표현식 사용)
            match = re.search(r'(\[\s*{.*?}\s*\])', text, re.DOTALL) # [ 와 ]로 감싸진, 내부에 { ... } 형태의 JSON 객체(또는 유사 구조)를 찾아내기 
            if match:
                json_text = match.group(1)
                items = json.loads(json_text)
            else:
                raise RuntimeError(f"JSON 배열을 찾을 수 없습니다.\nLLM 응답: {text}")
        except Exception as e:
            raise RuntimeError(f"JSON 파싱 실패: {e}\nLLM 응답: {text}")

        # 각 제품별 이름과 브랜드로 search_image_google 호출해 이미지 URL 채움
        for it in items:
            name = it.get("name", "")
            brand = it.get("brand", "")
            it["image_url"] = search_image_google(name, brand) or None
        print("DEBUG: 최종 items =", items)  # 이 로그로 실제 값 확인
        return items
    
    def prompt(self, question: str, context: str) -> str:
        system_prompt = PromptTemplate.from_template(
            """
            [System Instruction]
            당신은 건강기능식품 및 영양제 추천 전문가 AI입니다.  
            여러 문서를 분석해 사용자의 질문에 친절하고 이해하기 쉬운 말투로 답변하세요.  
            만약 사용자가 특정 증상(피로, 수면장애, 스트레스 등)을 이야기하면, 먼저 공감 문장으로 시작해 주세요.  
            예) "요즘 많이 힘드셨을 것 같아요."  
            정보가 없으면 "찾을 수 없습니다."라고 명확히 답변하세요.  
            절대로 추측하거나 거짓 정보를 만들지 마세요.

            답변은 아래 JSON 형식으로 정확히 3개의 제품 정보를 제공해야 합니다.  
            JSON 외 다른 텍스트는 출력하지 마세요.

            JSON 배열 각 원소는 다음 필드를 반드시 포함해야 합니다:
            - name: 제품명 (예: "멀티비타민 맥스")
            - brand: 제조사명 (예: "헬스코리아")
            - description: 제품명과 브랜드명을 언급한 후, 자연스럽고 친절한 어조로 제품의 주요 효능과 특징을 설명하세요. 질문에 따라 간결하게 답변하거나, 전문가적으로 답변해주세요.
            - usage: 섭취 방법 및 주의사항
            - precautions: 주의사항 내용을 간결하게 작성하세요.
            - storage: 보관 방법을 명확히 작성하세요.
            - expiration: 유통기한 정보를 정확히 기재하세요.
            - image_url: 빈 문자열("")로 둡니다 (이미지는 별도 API로 처리됩니다)

            예시:  
            [
            {{
                "name": "멀티비타민 맥스",
                "brand": "헬스코리아",
                "description": "멀티비타민 맥스는 헬스코리아의 인기 제품으로, 피로 회복과 면역력 증진에 탁월한 도움을 줍니다. 꾸준히 복용하면 건강 유지에 효과적입니다.",
                "usage": "1일 1회, 식후 복용하세요. 임산부는 전문가 상담 필수입니다.",
                "precautions": "주의사항",      
                "storage": "보관방법",        
                "expiration": "유통기한", 
                "image_url": ""
            }},
            ...
            ]

            [Context]
            {context}

            [Input]
            {question}
            """
        )
        return system_prompt.format(context=context, question=question)