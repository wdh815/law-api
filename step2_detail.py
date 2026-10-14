import requests

# 본문조회 API 주소. 목록조회(lawSearch)와 파일명이 다르다는 점에 주목.
BASE_URL = "https://www.law.go.kr/DRF/lawService.do"

# 단계 1에서 얻은 법령ID를 넣는다. (실제 실행 시 출력된 법령ID로 교체)
LAW_ID = "010199"

params = {
    "OC": "본인OC",     # 인증키
    "target": "law",    # 대상: 현행법령
    "ID": LAW_ID,       # 검색어가 아니라 '법령ID'로 콕 집어 현행 조문을 조회
    "type": "JSON",
}

response = requests.get(BASE_URL, params=params)
print("호출한 주소:", response.url)

# 단계 1과 같은 안전장치: JSON이 아니면 원문을, 오류 JSON이면 이유를 보여주고 멈춘다.
try:
    data = response.json()
except ValueError:
    raise SystemExit("JSON 응답이 아닙니다:\n" + response.text[:200])
if "result" in data:
    raise SystemExit(f"호출 실패: {data['result']} → OC·요청 IP 등록·승인 상태를 확인")

# 본문 JSON 구조는 {"법령": {"조문": {"조문단위": [ ... ]}}} 형태다.
units = data.get("법령", {}).get("조문", {}).get("조문단위", [])

# 조문이 1건이면 딕셔너리로 올 수 있어 리스트로 통일 (단계 1과 같은 안전장치)
if isinstance(units, dict):
    units = [units]

# 각 조문에서 '조문내용' 값을 꺼낸다.
for article in units:
    content = article.get("조문내용")
    if content:  # 조문내용이 있는 항목만 (비어 있으면 건너뛴다)
        print(content.strip())