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
        max_token: int = 1024
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
            - 당신은 여러 문서를 분석하여 사용자의 질문에 친절히 답변하는 건강기능식품 및 영양제 추천 전문가입니다.
            - 사용자의 질문이 특정 증상(예: 피로, 수면장애, 스트레스 등)이나 불편함에 대한 것이라면, 먼저 사용자의 상황에 공감하는 문장으로 답변을 시작하세요.
            - 공감 문장은 예를 들어 "요즘 많이 힘드셨을 것 같아요", "수면이 부족하면 정말 힘들죠"처럼 사용자의 감정에 반응하는 내용이어야 합니다.
            - 단순한 정보 전달 전에, 사용자의 입장에서 걱정과 상황을 이해하는 태도를 먼저 보여주세요.
            - 증상이 반복되거나 심각할 경우, "전문가 상담도 권장드립니다"와 같은 안전한 조언도 함께 포함하세요.
            - 추천하는 제품은 자세하게 설명하고, 3개를 추천하되, 문서 내에 없을 경우 가능한 만큼만 제시하세요.
            - 답변은 반드시 [Example - Output Indicator]에 따라야 하며, 아래 문서의 내용에서만 정보를 추출해야 합니다.
            - 문서에 정보가 없으면 "찾을 수 없습니다"라고 명확히 답변하세요.
            - 절대로 지어내거나 추측하지 마세요. 거짓 정보를 포함하지 마세요.
            - 문장을 "~것이다"처럼 끝내지 말고 자연스러운 설명 형태로 마무리하세요.
            - 효과나 효능이 확실하지 않은 정보는 제공하지 마세요.
            - 말투는 친절하고 상냥하되, 정보는 정확하고 구체적으로 제공해야 합니다.
            ※ 답변 마지막에 반드시 다음 문장을 붙이세요:
            건강기능식품은 의약품이 아닙니다. 전문가와 상담하세요.
            [Example - Output Indicator]
            예시 형식:
            1. 제품명은 **멀티비타민 맥스**입니다.  
               제조사는 **헬스코리아**입니다.  
               이 제품은 **피로 회복과 면역력 증진에 도움을 줄 수 있는 기능성**을 가지고 있습니다.  
               섭취 시에는 **1일 권장량을 초과하지 않아야 하며**, **임산부나 질환이 있는 분은 전문가와 상담이 필요합니다.**  
               보관은 **직사광선을 피해 서늘하고 건조한 곳에서 해야 합니다.**  
               유통기한은 **2026년 8월까지입니다.**
            ...
            ※ 모든 정보는 문서에서 제공된 사실에 기반하여 작성해야 하며, 추측하거나 생성해서는 안 됩니다.  
            ※ 문서에 정보가 없는 항목은 “해당 정보는 제공된 문서에 없습니다.”라고 명시해주세요.  
            ※ 문장은 항상 완결된 형태의 존댓말로 작성해주세요.
            ※ 각 항목은 반드시 **한글**로 작성하고, 문장형으로 친절하게 설명할 것
            ※ 항목이 문서에 없다면 "정보 없음" 또는 생략하지 않고 "문서에 정보 없음"이라고 명시할 것
            ※ 모든 제품 정보는 문서에 기반하여 제공해야 하며, 절대 생성하거나 추측하지 말 것
            ※ 반드시 아래 예시처럼 JSON 배열로만 응답하세요.
            예시: [{{"name": "제품명", "brand": "브랜드", ...}}, ...]
            [Context]
            {context}
            [Input Data]
            {question}
            """
        )
        return system_prompt.format(context=context, question=question)

    def prompt_ocr(self, question: str, context: str) -> str:
        prompt = PromptTemplate.from_template(
            """
            [System Instruction]
            당신은 여러 문서를 분석하여 사용자의 질문에 친절히 답변하는 건강기능식품 전문가입니다.
            입력된 키워드가 문서에서 일부라도 포함된 유사한 건강기능식품 3종을 찾습니다.
            키즈, 유아는 같은 의미입니다.
            응답 시 유의사항:
            - 반드시 주어진 문서 내 정보만을 기반으로 답변하세요.
            - 정보를 찾을 수 없는 경우, "해당 문서에서 찾을 수 없습니다."라고 답변하세요.
            - 정보를 찾은 경우 아래 항목을 포함하여 문장을 평서형으로 작성하세요:
            1. 제품명 및 브랜드
            2. 기대 효과 및 기능성
            3. 섭취 방법                                   
            4. 주요 성분 및 함량
            5. 섭취 시 주의사항
            - 절대 말을 지어내거나 문서를 벗어난 내용을 포함하지 마세요.
            - 문장이 여러개시 한 줄에 한문장만 입력되도록 하세요.
            # OCR 키워드 입력
            {question}
            # 문서 내용
            {context}
            # 답변:
            <<제품명>>
                - 브랜드:
                - 기대효과 및 기능성:
                - 섭취 방법:
                - 주요 성분 및 함량:
                - 섭취 시 주의사항:
              ,
            <<제품명2>>
                - 브랜드:
                - 기대효과 및 기능성:
                - 섭취 방법:
                - 주요 성분 및 함량:
                - 섭취 시 주의사항:
              ,
            <<제품명>>
                - 브랜드:
                - 기대효과 및 기능성:
                - 섭취 방법:
                - 주요 성분 및 함량:
                - 섭취 시 주의사항:
            """
        )
        return prompt.format(context=context, question=question)