# law-api — 법제처 법령정보 Open API 수집 (6주차 실습)

법제처 국가법령정보 Open API로 **검색 → 법령ID → 본문 → FastAPI 서버 → SQLite 캐시** 파이프라인을 만든 실습이다. 단계 0~5까지 진행했다.

| 파일 | 역할 |
|---|---|
| `step1_search.py` | 목록조회(`lawSearch.do`)로 법령명 검색 → 법령ID 얻기 |
| `step2_detail.py` | 본문조회(`lawService.do`)에 법령ID를 넘겨 현행 조문 가져오기 |
| `law_client.py` | 위 두 호출을 `search_law`·`get_law_detail` 함수로 정리, 인증키는 `.env`에서 읽음 |
| `explore.py` | 응답 JSON을 들여쓰기해 통째로 찍어 구조 확인 |
| `main.py` | FastAPI 서버 — `/search`, `/detail/{law_id}` (DB 캐시 포함) |
| `db.py` | SQLite `laws`·`articles` 테이블 생성·저장·조회 |

> 실행하려면 `.env`에 `LAW_OC=본인OC` 한 줄이 필요하다. `step1_search.py`·`step2_detail.py`·`explore.py`는 `.env`를 읽지 않으므로 파일 안의 `"본인OC"`를 직접 바꿔서 실행한다.

## ① 결과 확인

- **검색 → 본문:** `law_client`로 `개인정보 보호법`을 검색하니 `[{'name': '개인정보 보호법', 'law_id': '011357'}, {'name': '개인정보 보호법 시행령', 'law_id': '011468'}]`가 나왔고, `get_law_detail('011357')`로 조문 141개를 받아왔다. 첫 줄은 `제1장 총칙`, 이어서 `제1조(목적) 이 법은 개인정보의 처리 및 보호에 관한 사항을…`가 나왔다.
- **캐시:** 서버를 켜고 `/detail/011357`을 두 번 호출했다.
  - 1번째: `"source": "api(law.go.kr)"`, `article_count: 141` → 법제처에서 받아와 DB에 저장
  - 2번째: `"source": "db(cache)"`, `fetched_at: 2026-10-14T20:43:42`, `name: ""` → DB에서 바로 응답
  - 응답을 만든 곳이 바뀌니 키 구성도 다르다(`article_count` 대신 `fetched_at`·`name`). 처음에 해 본 `010199`(전자금융거래법)도 같은 방식으로 캐시됐다.

## ② 핵심 개념 되새김

- **인증키(OC):** 법제처가 "누가, 승인된 IP에서 부르는지" 확인하는 신분증이다. 서버는 요청 하나하나를 독립적으로 처리하고 이전 요청을 기억하지 않으므로, 매 요청에 OC를 붙여야 한다.
- **목록조회 → 상세조회 2단 구조:** 목록조회는 이름으로 찾아서 법령ID 같은 식별자만 주고, 본문은 그 ID로 상세조회를 따로 불러야 온다. 검색 결과는 가볍게, 본문은 필요한 것만 받는 구조다.
- **DB 캐시 이유:** 같은 법령을 다시 물을 때 법제처를 또 부르지 않으니 응답이 빠르고 호출량(트래픽·한도)을 아낀다. 언제 받았는지(`fetched_at`) 같은 이력도 쌓인다.

## ③ 자유 로그

- OC는 미리 신청해 둔 본인 키가 승인돼서 `test` 없이 처음부터 본인 OC로 진행했다. 브라우저 호출 → `step1`에서 `전자금융거래법 / 010199`, `전자금융거래법 시행령 / 010366` 두 줄이 나오는 것까지 바로 됐다.
- **explore.py로 본 응답 구조:** 최상위는 `LawSearch` 하나이고, 그 안에 `totalCnt`·`page`·`numOfRows`·`resultCode` 같은 메타 정보와 `law` 목록이 있다. `law` 항목 하나에 키가 16개나 있다. `법령일련번호`(290247)는 위쪽에, `법령ID`(010199)는 한참 아래에 떨어져 있었다. `법령상세링크`의 `MST=290247`이 바로 법령일련번호다. 일련번호는 개정본마다 바뀌고 법령ID는 그대로라서, 본문조회에는 법령ID를 넣어야 늘 현행본이 온다.
- **막힌 곳:** `python db.py`에서 `IndentationError: expected an indented block after function definition`이 났다. 코드를 붙여넣다가 `def save_law`·`def load_law` 줄이 4칸 들여써져서 `init_db` 안의 함수로 읽힌 것이었다. 두 `def`를 맨 왼쪽으로 옮겨 해결했다. 에러가 난 줄만 보지 말고 바로 위 `def` 줄의 들여쓰기부터 봐야 한다는 걸 배웠다.
- **제출 전 점검에서 발견:** `.gitignore`를 만들어만 두고 내용이 비어 있었다. 또 `step1`·`step2`·`explore`에는 실제 OC가 그대로 들어 있었다. 그대로 `git add .` 했으면 키와 `law.db`가 올라갈 뻔했다. `.gitignore`를 채우고 세 파일의 OC를 `"본인OC"`로 되돌린 뒤 `git status`로 `.env`가 빠진 것을 확인하고 커밋했다.
- **아직 안 해 본 것:** 조문이 제목·첫 줄만 나오는 문제(항·호 이어붙이기, 4장 심화)와, 검색 결과가 20건을 넘을 때 `display`·`page`로 넘기는 것. 캐시도 지금은 한 번 저장하면 개정이 있어도 갱신되지 않아서, 유효기간을 두는 방법이 궁금하다.
- **AI 활용:** Claude Code에게 `db.py`의 IndentationError 원인 분석을 맡겼다. 이어서 제출 전 정리(OC 되돌리기·.gitignore 채우기)와 README 초안, GitHub 업로드도 시켰다. 검증은 이렇게 했다: `python db.py`를 다시 실행해 오류가 사라진 것을 확인했고, 서버를 켜서 같은 `/detail` 요청 두 번의 `source`가 api → db(cache)로 바뀌는 것을 직접 봤다. 커밋 전 `git status`와 `grep`으로 키가 어디에도 남지 않았는지도 확인했다.
