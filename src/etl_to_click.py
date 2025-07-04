#!/usr/bin/env python3
"""
ETL: Postgres ➜ ClickHouse
"""

import os
import time
import logging
import urllib.parse as u

import pandas.io.sql as psql
from clickhouse_connect import get_client
from dotenv import load_dotenv

from . import db                       
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)
log = logging.getLogger("etl2ch")

load_dotenv()

CH_DSN      = os.getenv("CH_DSN", "http://clickhouse:8123")
CH_USER     = os.getenv("CH_USER", "default")
CH_PASSWORD = os.getenv("CH_PASSWORD")

TRIES       = int(os.getenv("CH_WAIT_TRIES", 30))
PAUSE       = 2                              


def _make_client():
    p = u.urlparse(CH_DSN)
    host = p.hostname or "clickhouse"
    port = p.port or 8123
    log.debug("create client → %s:%s (user=%s)", host, port, CH_USER)
    return get_client(
        host=host,
        port=port,
        username=CH_USER,
        password=CH_PASSWORD,
    )


def wait_clickhouse() -> "Client":
    """Ждём HTTP-эндпоинт CH (`SELECT 1`)"""
    for n in range(1, TRIES + 1):
        try:
            cl = _make_client()
            cl.command("SELECT 1")
            log.info("ClickHouse UP (attempt %s)", n)
            return cl
        except Exception as exc:
            log.warning("CH not ready (attempt %s/%s): %s", n, TRIES, exc)
            time.sleep(PAUSE)
    raise RuntimeError(f"❌  CH недоступен после {TRIES*PAUSE} сек")


def main() -> None:
    log.info("⏳  Жду Postgres…")
    pg = db.get_conn()
    log.info("✅  PG OK")

    log.info("⏳  Читаю агрегат из PG…")
    df = psql.read_sql(
    """
    SELECT
        COALESCE(c.description, c.code) AS competency,   -- ← берём текст
        c.category                      AS category,
        s.type                          AS source,
        cs.frequency
    FROM competency_source cs
    JOIN competencies  c ON c.id = cs.competency_id
    JOIN sources       s ON s.id = cs.source_id 
    """,
    pg,
)
    log.info("📥  Из PG забрал %s строк", len(df))

    log.info("⏳  Жду ClickHouse…")
    ch = wait_clickhouse()

    ch.command("""
    CREATE TABLE IF NOT EXISTS competencies_olap (
        competency String,
        category   String,
        source     String,
        frequency  UInt32
    ) ENGINE = MergeTree
    ORDER BY (category, competency, source)
    """)

    ch.insert_df("competencies_olap", df)
    log.info("🚀  В ClickHouse залито %s строк", len(df))


if __name__ == "__main__":
    main()
