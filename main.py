from contextlib import asynccontextmanager

from fastapi import FastAPI
from law_client import search_law, get_law_detail
from db import init_db, save_law, load_law  # 방금 만든 DB 함수


# yield 앞은 서버가 뜰 때, yield 뒤는 서버가 내려갈 때 한 번씩 실행된다.
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()   # 부팅 시 딱 한 번 DB/테이블을 준비한다
    yield       # ← 여기서 서버가 요청을 받는다


app = FastAPI(lifespan=lifespan)

@app.get("/search")
def search(query: str):
    results = search_law(query)  # 검색은 매번 최신으로
    return {"count": len(results), "results": results}

@app.get("/detail/{law_id}")
def detail(law_id: str):
    cached = load_law(law_id)          # ① DB에 있나?
    if cached is not None:
        return {"source": "db(cache)", **cached}  # ② 있으면 DB에서 바로 응답

    articles = get_law_detail(law_id)  # ③ 없으면 법제처 호출
    save_law(law_id, "", articles)     # ④ DB에 저장(다음부터 캐시됨)
    return {"source": "api(law.go.kr)", "law_id": law_id,
            "article_count": len(articles), "articles": articles}