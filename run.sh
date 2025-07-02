#!/bin/sh
set -e

echo "⌛ wait PG (max 30s)…"
for i in $(seq 1 30); do
  pg_isready -h postgres -U fgos >/dev/null 2>&1 && break
  sleep 0.25
done

echo "FGOS"
python -m src.fgos_parser

echo "HH VACANCIES"
python -m src.hh         # ← имя файла hh.py

echo "ETL → ClickHouse"
python -m src.etl_to_click

echo "Done"
