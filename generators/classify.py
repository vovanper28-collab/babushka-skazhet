#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv, os, re

CSV_IN  = '/var/www/babushka-skazhet/table.csv'
OUT_DIR = '/var/www/babushka-skazhet/url-migration'
MAP_OUT = os.path.join(OUT_DIR, 'url-map.csv')

TRANS = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
    'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m',
    'н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u',
    'ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch',
    'ъ':'-','ы':'y','ь':'-','э':'e','ю':'yu','я':'ya',
}

def transliterate(word):
    result = ''
    for ch in word.lower():
        result += TRANS.get(ch, ch)
    result = re.sub(r'[^a-z0-9-]', '-', result)
    result = re.sub(r'-+', '-', result)
    return result.strip('-')

CATEGORIES = [
    ('sny',        ['снится','снил','приснил','сновид','во сне','сон ','снятся','снюсь']),
    ('zdorove',    ['здоров','болезн','болит','самочувств','недуг','хвор','температур',
                    'простуд','бессонниц','голов','давлен','уснут','устал','кашел',
                    'насморк','лечит','спорт','привычк','аллерг','иммунит','похуд',
                    'имт ','вес ','зрен','слух']),
    ('dengi',      ['деньг','богатств','доход','зарплат','прибыл','финанс','монет',
                    'купюр','разбогат','бизнес','копит','мечт','заработ','карьер',
                    'накопит','инвестиц','ипотек','кредит','работ','долг']),
    ('otnosheniya',['любов','муж','жен','парн','девушк','свадьб','семь','ребен','ребён',
                    'измен','жених','невест','брак','развод','свидан','отношен','поцелу',
                    'замуж','подруг','ссор','мирит','подрост','дочер','дочь','сын','сыном',
                    'половинк','новорожд','купат','воспит','школ','садик','дружб','дружить',
                    'друзья','детск','детей','детям','детьми']),
    ('primety',    ['чешет','разбил','рассып','примет','кошк','птиц','зеркал','соль',
                    'ложк','нож','ворон','паук','пятн','зев','встрет','увид','услыш',
                    'ладон','губ','ухо','бров','щек','прыщ','икот','чих','звон','свеч',
                    'посул','наступил','наткнул','потерял','нашел']),
]

def classify(query):
    q = query.lower()
    for cat, keys in CATEGORIES:
        for k in keys:
            if k in q:
                return cat
    return 'sovety'

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for c in ['primety','sny','otnosheniya','dengi','zdorove','sovety']:
        d = os.path.join(OUT_DIR, c)
        os.makedirs(d, exist_ok=True)
        for fn in os.listdir(d):
            os.remove(os.path.join(d, fn))

    with open(CSV_IN, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        rows = [r for r in reader if r and r[0].strip()]

    mapping, stats = [], {}
    for row in rows:
        query = row[0].strip()
        slug  = transliterate(query)
        cat   = classify(query)
        mapping.append((query, cat, f'/seo/{slug}.html', f'/{cat}/{slug}/'))
        stats[cat] = stats.get(cat, 0) + 1
        with open(os.path.join(OUT_DIR, cat, slug + '.txt'), 'w', encoding='utf-8') as out:
            out.write(query + '\n')

    with open(MAP_OUT, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['query','category','old_url','new_url'])
        w.writerows(mapping)

    print(f'Всего: {len(rows)}')
    for c, n in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'  {c:12s} {n}')
    print(f'\nurl-map: {MAP_OUT}')

if __name__ == '__main__':
    main()
