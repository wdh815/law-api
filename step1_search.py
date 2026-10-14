# requests: 인터넷 주소를 호출하기 위한 라이브러리
import requests

# 목록조회 API의 기본 주소. 이 뒤에 파라미터를 붙여 호출한다.
BASE_URL = "https://www.law.go.kr/DRF/lawSearch.do"

# API에 함께 보낼 파라미터들을 딕셔너리로 정리한다.
params = {
    "OC": "본인OC",      # 인증키 (API인증키관리 화면의 값으로 교체)
    "target": "law",     # 검색 대상: 현행법령
    "query": "전자금융거래법",  # 검색어
    "type": "JSON",      # 응답 형식: JSON
}

# requests.get으로 호출. params를 넘기면 ?OC=...&target=... 주소를 자동 완성해준다.
response = requests.get(BASE_URL, params=params)
print("호출한 주소:", response.url)  # 실제 호출 주소 확인(디버깅용)

# .json(): 응답을 파이썬 딕셔너리로 변환. 드물게 JSON이 아닌 응답(점검 안내 페이지 등)이
# 올 수 있어, 그때는 원문 앞부분을 보여주고 멈추도록 감싼다.
try:
    data = response.json()
except ValueError:
    raise SystemExit("JSON 응답이 아닙니다:\n" + response.text[:200])

# OC·요청 IP·승인이 잘못되면 법제처는 {"result": "...", "msg": "..."} 형태의 오류 JSON을 돌려준다.
# 그대로 두면 아래에서 결과 0건처럼 보이므로, 여기서 이유를 출력하고 멈춘다.
if "result" in data:
    raise SystemExit(f"호출 실패: {data['result']} → OC 값·요청 IP 등록·승인 상태를 확인")

# 법령 목록은 data["LawSearch"]["law"] 안에 리스트로 들어있다.
# .get()은 키가 없어도 에러 대신 기본값을 주어 더 안전하다.
law_list = data.get("LawSearch", {}).get("law", [])

# 결과가 1건이면 리스트가 아니라 딕셔너리로 올 수 있어 리스트로 통일한다.
if isinstance(law_list, dict):
    law_list = [law_list]

# 각 항목은 딕셔너리. 대괄호 키로 원하는 값을 꺼낸다.
for law in law_list:
    name = law["법령명한글"]   # 법령 이름
    law_id = law["법령ID"]     # 법령 고유 번호 (다음 단계 본문조회의 핵심 열쇠)
    print(f"법령명: {name} / 법령ID: {law_id}")