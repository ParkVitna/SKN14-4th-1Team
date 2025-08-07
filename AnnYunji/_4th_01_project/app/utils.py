import re

def parse_product_detail(raw_text):
    result = {}

    # 제품명 추출
    product_match = re.search(r"<<(.+?)>>", raw_text)
    if product_match:
        result["제품명"] = product_match.group(1).strip()

    # 항목 정의
    fields = [
        "브랜드",
        "기대효과 및 기능성",
        "섭취 방법",
        "주요 성분 및 함량",
        "섭취 시 주의사항"
    ]

    for i in range(len(fields)):
        start = fields[i]
        end = fields[i+1] if i + 1 < len(fields) else None

        if end:
            # 수정된 정규식
            pattern = rf"-?\s*{start}:\s*(.*?)(?=-?\s*{end}:|$)"
        else:
            pattern = rf"-?\s*{start}:\s*(.*)"

        match = re.search(pattern, raw_text, re.DOTALL)
        if match:
            value = match.group(1)
            value = re.sub(r'\s+', ' ', value).strip()
            value = re.sub(r'[-ㆍ·．・]*\s*$', '', value)
            result[start] = value

    # 키 변환
    parsed_clean = {
        "name": result.get("제품명", ""),
        "brand": result.get("브랜드", ""),
        "benefits": result.get("기대효과 및 기능성", ""),
        "how_to_take": result.get("섭취 방법", ""),
        "ingredients": result.get("주요 성분 및 함량", ""),
        "cautions": result.get("섭취 시 주의사항", "")
    }

    return parsed_clean
