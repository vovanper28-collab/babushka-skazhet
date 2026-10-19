#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

PROJECT = '/var/www/babushka-skazhet'
BASE_URL = 'https://babushka-skazhet.ru'

def process_file(filepath):
    # Вычисляем URL страницы по её пути
    rel_path = os.path.relpath(filepath, PROJECT)
    if rel_path == 'index.html':
        url = f'{BASE_URL}/'
    else:
        # замена \index.html на /
        page_path = rel_path.replace('\\', '/').replace('/index.html', '/')
        url = f'{BASE_URL}/{page_path}'
    
    # Читаем файл
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # Проверяем, нет ли уже canonical
    if 'rel="canonical"' in content:
        return 'skip'

    # Формируем тег
    canonical_tag = f'<link rel="canonical" href="{url}">\n'

    # Вставляем перед </head>
    if '</head>' not in content:
        return 'nohead'

    new_content = content.replace('</head>', canonical_tag + '</head>', 1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return 'ok'

def main():
    updated = 0
    skipped = 0
    errors = 0

    # Проходим по всем файлам index.html в проекте
    for root, dirs, files in os.walk(PROJECT):
        # Исключаем служебные папки
        if 'node_modules' in root or '.git' in root:
            continue
        
        if 'index.html' in files:
            filepath = os.path.join(root, 'index.html')
            result = process_file(filepath)
            
            if result == 'ok':
                updated += 1
            elif result == 'skip':
                skipped += 1
            else:
                errors += 1
                print(f'Ошибка в файле: {filepath}')

    print(f'Обновлено: {updated}')
    print(f'Пропущено (уже было): {skipped}')
    print(f'Ошибок: {errors}')

if __name__ == '__main__':
    main()
