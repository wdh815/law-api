import requests
import json  # 파이썬 데이터를 보기 좋게 출력하는 표준 라이브러리

url = "https://www.law.go.kr/DRF/lawSearch.do"
params = {"OC": "본인OC", "target": "law", "query": "전자금융거래법", "type": "JSON"}
resp = requests.get(url, params=params)
try:
    data = resp.json()
except ValueError:  # JSON이 아닌 응답(점검 페이지 등)이면 원문을 보여준다
    print("JSON 응답이 아닙니다:", resp.text[:200]); raise SystemExit

# ensure_ascii=False: 한글이 깨지지 않고 그대로 보이게
# indent=2: 2칸 들여쓰기로 계층 구조가 눈에 보이게
print(json.dumps(data, ensure_ascii=False, indent=2))