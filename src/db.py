import os, time, psycopg2
from dotenv import load_dotenv

load_dotenv()
DEFAULT_DSN = "postgres://fgos:fgos@postgres:5432/fgos"
PG_DSN = os.getenv("PG_DSN", DEFAULT_DSN)

_conn = None

def get_conn():
    """Подключаемся с 5-кратным ретраем, чтобы дождаться контейнер postgres."""
    global _conn
    if _conn and not _conn.closed:
        return _conn
    for _ in range(5):
        try:
            _conn = psycopg2.connect(PG_DSN)
            _conn.autocommit = True
            return _conn
        except psycopg2.OperationalError:
            time.sleep(2)
    raise RuntimeError("❌  Postgres недоступен, PG_DSN=%s" % PG_DSN)

def init_schema() -> None:
    """Создаем схему БД с обработкой ошибок"""
    try:
        with get_conn().cursor() as cur:
            cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'src_type') THEN
                    CREATE TYPE src_type AS ENUM ('ФГОС','Вакансия','Профстандарт');
                END IF;
            END$$;
            """)
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id         SERIAL PRIMARY KEY,
                code       VARCHAR(128) UNIQUE,
                type       src_type NOT NULL,
                url        TEXT,
                title      TEXT,
                fetched_at TIMESTAMPTZ DEFAULT now()
            );
            """)
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS competencies (
                id          SERIAL PRIMARY KEY,
                code        VARCHAR(128) UNIQUE,
                description TEXT,
                category    VARCHAR(8)
            );
            """)
            
            cur.execute("""
            CREATE TABLE IF NOT EXISTS competency_source (
                competency_id INT REFERENCES competencies(id),
                source_id     INT REFERENCES sources(id),
                frequency     INT NOT NULL DEFAULT 1,
                indicator     TEXT,
                PRIMARY KEY (competency_id, source_id)
            );
            """)
            
        print("✅ Схема БД создана успешно")
        
    except Exception as e:
        print(f"❌ Ошибка создания схемы: {e}")
        raise

def upsert_source(code: str, src_type: str, url: str, title: str | None = None) -> int:
    with get_conn().cursor() as cur:
        cur.execute("""
        INSERT INTO sources(code, type, url, title)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (code) DO UPDATE
            SET url = EXCLUDED.url,
                title = COALESCE(EXCLUDED.title, sources.title)
        RETURNING id
        """, (code, src_type, url, title))
        return cur.fetchone()[0]

def upsert_competency(code: str, desc: str | None, cat: str) -> int:
    with get_conn().cursor() as cur: 
        cur.execute("""
        INSERT INTO competencies(code, description, category)
        VALUES (%s,%s,%s)
        ON CONFLICT (code) DO UPDATE
            SET description = COALESCE(EXCLUDED.description, competencies.description),
                category    = competencies.category
        RETURNING id
        """, (code, desc, cat))
        return cur.fetchone()[0]

def link(comp_id: int, src_id: int) -> None:
    with get_conn().cursor() as cur: 
        cur.execute("""
        INSERT INTO competency_source(competency_id, source_id)
        VALUES (%s,%s)
        ON CONFLICT (competency_id, source_id) DO UPDATE
            SET frequency = competency_source.frequency + 1
        """, (comp_id, src_id))