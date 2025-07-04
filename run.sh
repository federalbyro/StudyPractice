#!/bin/sh
set -e

echo "⌛ wait PG …"
until pg_isready -h postgres -U fgos >/dev/null 2>&1 ; do
  sleep 0.5
done

echo "⌛ wait ClickHouse …"
until wget -qO- http://clickhouse:8123/ping >/dev/null 2>&1 ; do
  sleep 1
done

echo "FGOS"
python -m src.fgos_parser

echo "HH VACANCIES"
python -m src.hh

echo "ETL → ClickHouse"
python -m src.etl_to_click

echo "✅ Done"
