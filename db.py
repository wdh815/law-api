import sqlite3
from datetime import datetime

DB_FILE = "law.db"  # 실행하면 이 파일이 자동 생성된다.


def init_db():
    """DB와 테이블을 준비. 프로그램 시작 시 한 번 호출."""
    conn = sqlite3.connect(DB_FILE)  # DB 파일에 연결(없으면 생성)
    cur = conn.cursor()             # SQL을 실행하는 통로

    # IF NOT EXISTS: 이미 있으면 다시 만들지 않음(에러 방지)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS laws (
            law_id     TEXT PRIMARY KEY,   -- 법령ID(고유값). 중복 저장 방지.
            name       TEXT,               -- 법령명
            fetched_at TEXT                -- 조회한 시각
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,  -- 자동 증가 번호
            law_id   TEXT,                               -- 어느 법령의 조문인지
            content  TEXT                                -- 조문 내용
        )
    """)
    conn.commit()  # 변경을 파일에 실제로 저장
    conn.close()

def save_law(law_id, name, articles):
    """법령 1건과 그 조문들을 저장."""
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()

    # INSERT … ON CONFLICT DO UPDATE(UPSERT): 같은 law_id가 이미 있으면 그 행의 name·fetched_at만 갱신한다.
    # excluded = "방금 넣으려던 새 값". ?는 값 자리표시자(안전). PostgreSQL에서도 같은 문법.
    cur.execute(
        "INSERT INTO laws (law_id, name, fetched_at) VALUES (?, ?, ?) "
        "ON CONFLICT(law_id) DO UPDATE SET name = excluded.name, fetched_at = excluded.fetched_at",
        (law_id, name, datetime.now().isoformat()),
    )
    # 이 법령의 기존 조문을 먼저 지운다(재조회 시 중복 쌓임 방지)
    cur.execute("DELETE FROM articles WHERE law_id = ?", (law_id,))
    for content in articles:
        cur.execute("INSERT INTO articles (law_id, content) VALUES (?, ?)", (law_id, content))

    conn.commit(); conn.close()

def load_law(law_id):
    """저장된 법령과 조문을 꺼내온다. 없으면 None."""
    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()

    cur.execute("SELECT law_id, name, fetched_at FROM laws WHERE law_id = ?", (law_id,))
    row = cur.fetchone()  # 결과가 있으면 튜플 1개, 없으면 None
    if row is None:
        conn.close(); return None

    cur.execute("SELECT content FROM articles WHERE law_id = ?", (law_id,))
    articles = [r[0] for r in cur.fetchall()]  # 각 행의 첫 값(content)만 추출
    conn.close()
    return {"law_id": row[0], "name": row[1], "fetched_at": row[2], "articles": articles}


# 이 파일을 직접 실행하면 DB와 테이블을 만든다(실습의 첫 단계).
if __name__ == "__main__":
    init_db()
    print("law.db 준비 완료 — 테이블이 생성되었습니다.")