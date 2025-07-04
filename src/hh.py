# hh.py
"""
Получает key-skills по списку URL-ов вакансий HeadHunter,
используя публичный API hh.ru/vacancies/{id}.
Выводит результат в консоль.  ─ Dry-run, без БД.

Запуск:  python hh.py
"""

import re
import time
import random
import requests
import sys
import os
from urllib.parse import urlparse

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from . import db

VACANCY_URLS = [
    "https://hh.ru/vacancy/122108823?query=Frontend&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122243382?query=Frontend&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122225475?query=Frontend&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122160338?query=Frontend&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122207364?query=Frontend&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/117442704?query=Frontend&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122062524?query=Data+Engineer&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/120766762?query=Data+Engineer&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122195307?query=Data+Engineer&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122228096?query=%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D1%8B%D0%B9+%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122179134?query=%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D1%8B%D0%B9+%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122096369?query=%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D1%8B%D0%B9+%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121857105?query=%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D1%8B%D0%B9+%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/120292712?hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121933473?hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122220017?from=applicant_recommended&hhtmFrom=main",
    "https://hh.ru/vacancy/122051800?from=applicant_recommended&hhtmFrom=main",
    "https://hh.ru/vacancy/122267878?from=applicant_recommended&hhtmFrom=main",
    "https://hh.ru/vacancy/122223103?from=applicant_recommended&hhtmFrom=main",
    "https://hh.ru/vacancy/121306927?query=Golang&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121229681?query=Golang&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121718067?query=Golang&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121917432?query=Golang&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/120706820?query=Golang&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122042165?query=Golang&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122084620?query=Golang&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121395072?query=Kotlin&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121896544?query=Kotlin&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121301944?query=Kotlin&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122024686?query=Kotlin&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/120065726?query=Kotlin&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121727831?query=Kotlin&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/119729432?query=DevOps&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121595225?query=DevOps&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/120706820?query=DevOps&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122277768?query=DevOps&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121346482?query=DevOps&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122261626?query=DevOps&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122225475?query=DevOps&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/120928790?query=%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122178909?query=%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121784829?query=%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122204059?query=%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122159617?query=%D1%82%D0%B5%D1%81%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D1%89%D0%B8%D0%BA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/122132252?query=%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B5+%D0%BE%D0%B1%D0%B5%D1%81%D0%BF%D0%B5%D1%87%D0%B5%D0%BD%D0%B8%D0%B5&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121288161?query=%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B5+%D0%BE%D0%B1%D0%B5%D1%81%D0%BF%D0%B5%D1%87%D0%B5%D0%BD%D0%B8%D0%B5&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121218658?query=%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B5+%D0%BE%D0%B1%D0%B5%D1%81%D0%BF%D0%B5%D1%87%D0%B5%D0%BD%D0%B8%D0%B5&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121843574?query=QA&hhtmFrom=vacancy_search_list",
    "https://hh.ru/vacancy/121665802?query=QA&hhtmFrom=vacancy_search_list",
]

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA}

ID_RE = re.compile(r"/vacancy/(\d+)")

def extract_id(url: str) -> str | None:
    """Вырезает числовой id вакансии из URL."""
    m = ID_RE.search(urlparse(url).path)
    return m.group(1) if m else None

def fetch_skills(vac_id: str) -> list[str]:
    """Берёт key_skills через API. Возвращает список (может быть пустым)."""
    api_url = f"https://api.hh.ru/vacancies/{vac_id}"
    resp = requests.get(api_url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return [ks["name"] for ks in data.get("key_skills", [])]

def fetch_vacancy_json(vac_id: str) -> dict:
    api_url = f"https://api.hh.ru/vacancies/{vac_id}"
    r = requests.get(api_url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()

def main() -> None:
    print("🔧 Инициализация схемы БД...")
    try:
        db.init_schema()
        print("✅ Схема БД успешно создана")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return

    print(f"🚀 Начинаем обработку {len(VACANCY_URLS)} вакансий...")
    
    processed = 0
    errors = 0
    
    for i, url in enumerate(VACANCY_URLS, 1):
        vac_id = extract_id(url)
        if not vac_id:
            print(f"\n[{i}/{len(VACANCY_URLS)}] {url}\n⚠️ id не распознан")
            errors += 1
            continue

        try:
            print(f"\n[{i}/{len(VACANCY_URLS)}] Обрабатываем вакансию {vac_id}...")
            data = fetch_vacancy_json(vac_id)
            skills = [k["name"] for k in data.get("key_skills", [])]
            title = data.get("name")

            src_id = db.upsert_source(f"VAC-{vac_id}", 'Вакансия', url, title)

            for sk in skills:
                comp_id = db.upsert_competency(sk, None, 'SKILL')
                db.link(comp_id, src_id)

            print(f"📋 {title}")
            print(f"🔧 Навыки: {', '.join(skills) if skills else '— навыков не найдено'}")
            processed += 1
            
        except Exception as ex:
            print(f"\n[{i}/{len(VACANCY_URLS)}] {url}\n⚠️ Ошибка: {ex}")
            errors += 1

        time.sleep(random.uniform(0.3, 0.8))

    print(f"\n🎯 Обработка завершена:")
    print(f"   ✅ Успешно: {processed}")
    print(f"   ❌ Ошибок: {errors}")
    print(f"   📊 Всего: {len(VACANCY_URLS)}")

if __name__ == "__main__":
    main()