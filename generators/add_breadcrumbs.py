#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, os, csv

PROJECT = '/var/www/babushka-skazhet'
MAP_IN  = os.path.join(PROJECT, 'url-migration/url-map.csv')
BASE = 'https://babushka-skazhet.ru'

CATS = {
    'primety':     'Приметы',
    'sny':         'Сны',
    'otnosheniya': 'Отношения и семья',
    'dengi':       'Деньги и достаток',
    'zdorove':     'Здоровье',
    'sovety':      'Советы на каждый день',
}

def make_jsonld(cat, cat_name, query, slug):
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": f"{BASE}/{cat}/"},
            {"@type": "ListItem", "position": 3, "name": query, "item": f"{BASE}/{cat}/{slug}/"},
        ]
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>\n'

def process_file(path, jsonld_html):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    if 'BreadcrumbList' in content:
        return 'skip'
    if '</head>' not in content:
        return 'nohead'
    new_content = content.replace('</head>', jsonld_html + '</head>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return 'ok'

# === SEO-страницы ===
updated = skipped = errors = 0
with open(MAP_IN, encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)
    for row in reader:
        if len(row) < 4: continue
        url = row[3].strip().strip('/')
        parts = url.split('/')
        if len(parts) != 2: continue
        cat, slug = parts
        if cat not in CATS: continue
        path = os.path.join(PROJECT, cat, slug, 'index.html')
        if not os.path.isfile(path):
            errors += 1
            continue
        jl = make_jsonld(cat, CATS[cat], row[0].strip(), slug)
        r = process_file(path, jl)
        if r == 'ok': updated += 1
        elif r == 'skip': skipped += 1
        else: errors += 1

# === Хабы ===
hub_updated = hub_skipped = 0
for cat, cat_name in CATS.items():
    path = os.path.join(PROJECT, cat, 'index.html')
    if not os.path.isfile(path): continue
    jl = make_jsonld(cat, cat_name, cat_name, '')  # для хаба позиция 3 = сама категория
    # Переделываем под хаб: убираем 3-й элемент
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": cat_name, "item": f"{BASE}/{cat}/"},
        ]
    }
    jl = '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>\n'
    r = process_file(path, jl)
    if r == 'ok': hub_updated += 1
    elif r == 'skip': hub_skipped += 1

print(f'SEO-страниц обновлено: {updated}')
print(f'SEO-страниц пропущено: {skipped}')
print(f'SEO-страниц с ошибкой: {errors}')
print(f'Хабов обновлено: {hub_updated}')
print(f'Хабов пропущено: {hub_skipped}')
