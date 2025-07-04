# Анализ компетенций: ФГОС ↔ Вакансии

Этот проект собирает профессиональные компетенции из Федеральных государственных образовательных стандартов (ФГОС) и вакансий HeadHunter, сохраняет их в PostgreSQL, агрегирует в ClickHouse и визуализирует в Grafana.

---

## 🚀 Структура

- `src/`
  - `db.py` — инициализация схемы и upsert-функции для PostgreSQL  
  - `fgos_parser.py` — парсер ФГОС-страниц  
  - `hh.py` — сбор key_skills из HH-вакансий  
  - `etl_to_click.py` — экспорт агрегаций из Postgres в ClickHouse  
- `run.sh` — последовательный запуск всех этапов  
- `docker-compose.yml` — контейнеры PostgreSQL, ClickHouse, Grafana, Parser  
- `.env` — переменные окружения (DSN и пароли)  
- `requirements.txt` — Python-зависимости  

---

## 📋 Быстрый старт

1. **Клонируйте репозиторий**  
```bash
   git clone https://…/competencies-analytica.git
   cd competencies-analytica
```

```bash
    # Создайте файл .env (пример ниже)
    PG_DSN=postgres://fgos:fgos@postgres:5432/fgos
    CH_DSN=http://clickhouse:8123
    CH_USER=default
    CH_PASSWORD=ch_pass
    CH_WAIT_TRIES=30
```

```bash
# Запустите весь стек через Docker Compose
docker compose up --build

# Контейнер parser автоматически выполнит:
fgos_parser.py → заполнит таблицы sources, competencies, competency_source в Postgres
hh.py → добавит данные из HH
etl_to_click.py → перенесёт агрегаты в ClickHouse
```

### Откройте Grafana
```bash
URL: http://localhost:3000

Логин/пароль: admin / admin (или заданы в docker-compose.yml)

Источник данных: ClickHouse

Дашборд: Import JSON или создайте вручную
```

## 🛠️ Локальный запуск (без Docker)


```bash
#Установите Python 3.12+ и зависимости:
pip install -r requirements.txt
```


```bash
# Запустите парсеры и ETL по шагам:
python -m src.fgos_parser
python -m src.hh
python -m src.etl_to_click
```

## 🌐 Дашборд Grafana

```bash
1. SELECT
  source,
  sum(frequency) AS freq
FROM competencies_olap
GROUP BY source
ORDER BY freq DESC
# - скрипт на соотношение навыков - Bar Chat 

2. SELECT
    competency,
    sum(frequency) AS freq
FROM competencies_olap
WHERE source = 'Вакансия'
  AND category = 'SKILL'
GROUP BY competency
HAVING freq <= 2               
ORDER BY competency
LIMIT 10
# топ-10 редких навыков с вакансий Bar Chart

3. SELECT
    competency,
    sum(frequency) AS freq
FROM competencies_olap
WHERE source = 'Вакансия'
  AND category = 'SKILL'
GROUP BY competency
ORDER BY freq DESC
LIMIT 10

#топ 10 популярных навыков с вакансий - Bar Chart


4. 

SELECT
    competency,           
    sum(frequency) AS freq
FROM competencies_olap
WHERE source   = 'ФГОС'
  AND category = 'ОПК'
GROUP BY competency
ORDER BY freq DESC
LIMIT 3


#топ 3 ОПК - TABLE

5.


SELECT
    competency,           
    sum(frequency) AS freq
FROM competencies_olap
WHERE source   = 'ФГОС'
  AND category = 'ПК'
GROUP BY competency
ORDER BY freq DESC
LIMIT 3

#топ 3 ПК - TABLE
```

## Полезные команды

```bash
docker compose logs -f parser
#Подключиться к ClickHouse CLI:

docker compose exec clickhouse clickhouse-client
#Очистить и пересобрать схему Postgres:

docker compose exec parser python -c "from src.db import init_schema; init_schema()"
```

## 🔑 Переменные окружения
```bash
# Переменная	Описание	Пример
PG_DSN	DSN для подключения к PostgreSQL	postgres://fgos:fgos@postgres:5432/fgos
CH_DSN	HTTP-URL ClickHouse	http://clickhouse:8123
CH_USER	Пользователь ClickHouse	default
CH_PASSWORD	Пароль ClickHouse	ch_pass
CH_WAIT_TRIES	Кол-во попыток дождаться ClickHouse (ETL)	30
```


# 🎯 Результаты
## PostgreSQL — нормализованная схема competencies × sources
## ClickHouse — ускорённая OLAP-таблица competencies_olap
## Grafana — интерактивные дашборды Top-N, source-split, дыры в ФГОС
