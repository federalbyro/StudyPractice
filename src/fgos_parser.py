# fgos_parser.py
"""
Сухой парсер трёх ФГОС-страниц.
Выводит все найденные ОПК-/ПК-компетенции в терминал.
Запуск:  python fgos_dryrun.py
"""

import re, requests
from bs4 import BeautifulSoup
from .db import init_schema, upsert_source, upsert_competency, link

URLS = [
    "https://fgos.ru/fgos/fgos-09-03-04-programmnaya-inzheneriya-229/",
    "https://fgos.ru/fgos/fgos-09-03-03-prikladnaya-informatika-207/",
    "https://fgos.ru/fgos/fgos-02-03-03-matematicheskoe-obespechenie-i-administrirovanie-informacionnyh-sistem-222/",
]

CODE_RE = re.compile(r"\b(О?ПК-\d+)\b")
DESC_RE = re.compile(r"([^.();:]+?)\s*\((О?ПК-\d+)\)")

def extract(url: str):
    html = requests.get(url, timeout=20).text
    soup = BeautifulSoup(html, "lxml")

    container = (
        soup.select_one("article")          # 
        or soup.select_one("div.entry-content")
        or soup.select_one("main")
        or soup                          
    )
    text = container.get_text(" ", strip=True)

    seen = set()
    for m in DESC_RE.finditer(text):
        desc, code = m.groups()
        if code not in seen:
            yield code, desc.strip(" ,.;")
            seen.add(code)

def main():
    init_schema()
    for url in URLS:
        src_code = f"FGOS-{url.split('/')[4]}"          
        src_id   = upsert_source(src_code, 'ФГОС', url, title=None)

        print(f"\n=== {url} ===")
        for code, desc in extract(url):
            comp_id = upsert_competency(code, desc, 'ПК' if code.startswith('ПК') else 'ОПК')
            link(comp_id, src_id)
            print(f"{code:<6} — {desc}")

if __name__ == "__main__":
    main()
