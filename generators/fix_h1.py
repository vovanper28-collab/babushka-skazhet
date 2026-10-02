#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re

PROJECT = '/var/www/babushka-skazhet'
CATEGORIES = ['primety', 'sny', 'otnosheniya', 'dengi', 'zdorove', 'sovety']

# Regex: ищем <h1>...</h1> ТОЛЬКО внутри <div id="mobile-header">
pattern = re.compile(
    r'(<div id="mobile-header">\s*)<h1>(.*?)</h1>',
    re.DOTALL
)

def process_file(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    if 'h1-mobile' in content:
        return False  # уже обработан
    new_content, n = pattern.subn(
        r'\1<div class="h1-mobile" role="heading" aria-level="1">\2</div>',
        content
    )
    if n == 0:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

updated = 0
for cat in CATEGORIES:
    cat_path = os.path.join(PROJECT, cat)
    if not os.path.isdir(cat_path):
        continue

    # Хаб-страница
    hub = os.path.join(cat_path, 'index.html')
    if os.path.isfile(hub) and process_file(hub):
        updated += 1

    # SEO-страницы
    for slug in os.listdir(cat_path):
        fpath = os.path.join(cat_path, slug, 'index.html')
        if os.path.isfile(fpath) and process_file(fpath):
            updated += 1

print(f'Обновлено файлов: {updated}')
