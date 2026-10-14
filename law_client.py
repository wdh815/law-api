import os

import requests
from dotenv import load_dotenv

load_dotenv()                # 같은 폴더의 .env를 읽어 환경변수로 올린다
OC = os.getenv("LAW_OC")     # .env의 LAW_OC 값. 없으면 None
if not OC:                    # 빈 값으로 호출하면 원인을 찾기 어려우니 여기서 멈춘다
    raise SystemExit(".env에 LAW_OC=내OC 한 줄을 넣어주세요 (5.3절)")

def search_law(query):
    """법령명을 검색해 [{name, law_id}] 목록을 돌려준다."""
    url = "https://www.law.go.kr/DRF/lawSearch.do"
    params = {"OC": OC, "target": "law", "query": query, "type": "JSON"}
    resp = requests.get(url, params=params)
    try:
        data = resp.json()
    except ValueError:  # JSON이 아닌 응답(점검 페이지 등)이면 원문을 보여주고 멈춘다
        raise SystemExit("JSON 응답이 아닙니다:\n" + resp.text[:200])
    if "result" in data:  # OC·요청 IP·승인 오류는 {"result","msg"} 형태의 JSON으로 온다
        raise SystemExit(f"호출 실패: {data['result']} — OC·요청 IP 등록·승인 상태를 확인하세요")

    law_list = data.get("LawSearch", {}).get("law", [])
    if isinstance(law_list, dict):
        law_list = [law_list]

    results = []
    for law in law_list:
        results.append({
            "name": law["법령명한글"],
            "law_id": law["법령ID"],   # 법령 고유 번호
        })
    return results

def get_law_detail(law_id):
    """법령ID로 현행 조문 내용 리스트를 돌려준다."""
    url = "https://www.law.go.kr/DRF/lawService.do"
    params = {"OC": OC, "target": "law", "ID": law_id, "type": "JSON"}
    resp = requests.get(url, params=params)
    try:
        data = resp.json()
    except ValueError:  # JSON이 아닌 응답(점검 페이지 등)이면 원문을 보여주고 멈춘다
        raise SystemExit("JSON 응답이 아닙니다:\n" + resp.text[:200])
    if "result" in data:  # OC·요청 IP·승인 오류는 {"result","msg"} 형태의 JSON으로 온다
        raise SystemExit(f"호출 실패: {data['result']} — OC·요청 IP 등록·승인 상태를 확인하세요")
    if "Law" in data:  # 없는 법령ID를 넣으면 {"Law": "일치하는 법령이 없습니다…"}가 온다
        raise SystemExit(f"조회 실패: {data['Law']} — 법령일련번호가 아니라 법령ID를 넣었는지 확인하세요")

    units = data.get("법령", {}).get("조문", {}).get("조문단위", [])
    if isinstance(units, dict):
        units = [units]

    articles = []
    for article in units:
        content = article.get("조문내용")  # 조문의 첫 줄만 (항·호 본문은 4장 심화 참고)
        if content:
            articles.append(content.strip())
    return articles

# 이 파일을 직접 실행할 때만 아래 테스트가 실행된다.
# (단계 4에서 main.py가 import할 때는 실행되지 않게 막아주는 관용 구문)
if __name__ == "__main__":
    found = search_law("전자금융거래법")
    print(found)
    print(get_law_detail(found[0]["law_id"])[:3])