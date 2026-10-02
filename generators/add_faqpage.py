#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, csv, os

PROJECT = '/var/www/babushka-skazhet'
CSV_IN  = os.path.join(PROJECT, 'table.csv')
MAP_IN  = os.path.join(PROJECT, 'url-migration/url-map.csv')

# 1. Загрузить все ответы из table.csv в dict
answers = {}
with open(CSV_IN, encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        if row and len(row) >= 2:
            answers[row[0].strip()] = row[1].strip()

print(f'Загружено ответов из CSV: {len(answers)}')

def make_faq_jsonld(query, answer):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": query,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            }
        ]
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>\n'

def process_file(path, jsonld_html):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    if 'FAQPage' in content:
        return 'skip'
    if '</head>' not in content:
        return 'nohead'
    new_content = content.replace('</head>', jsonld_html + '</head>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return 'ok'

updated = skipped = errors = no_answer = 0
with open(MAP_IN, encoding='utf-8') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader)
    for row in reader:
        if len(row) < 4: continue
        query = row[0].strip()
        url = row[3].strip().strip('/')
        parts = url.split('/')
        if len(parts) != 2: continue
        cat, slug = parts
        path = os.path.join(PROJECT, cat, slug, 'index.html')
        if not os.path.isfile(path):
            errors += 1
            continue
        answer = answers.get(query)
        if not answer:
            no_answer += 1
            continue
        jl = make_faq_jsonld(query, answer)
        r = process_file(path, jl)
        if r == 'ok': updated += 1
        elif r == 'skip': skipped += 1
        else: errors += 1

print(f'SEO-страниц обновлено: {updated}')
print(f'Пропущено (уже было): {skipped}')
print(f'Без ответа в CSV: {no_answer}')
print(f'Ошибок (нет файла): {errors}')
