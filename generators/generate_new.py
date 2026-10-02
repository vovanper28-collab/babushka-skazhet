#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv, os

PROJECT = '/var/www/babushka-skazhet'
CSV_IN  = os.path.join(PROJECT, 'table.csv')
MAP_IN  = os.path.join(PROJECT, 'url-migration/url-map.csv')

METRIKA = '''<!-- Yandex.Metrika counter -->
<script type="text/javascript">
   (function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
   m[i].l=1*new Date();
   for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
   k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
   (window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
   ym(113043800, "init", {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/113043800" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->'''

TEMPLATE = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
__METRIKA__
<link rel="stylesheet" href="/styles/style.css">
<meta name="yandex-verification" content="67a67b968299de38" />
</head>
<body class="seo-page">

<!-- Мобильная версия -->
<div id="mobile-wrapper">
<div id="mobile-header">
<h1><span class="brand">БабушкаСкажет:</span> __QUERY__</h1>
<div class="subhead">Обниму словом, успокою душу</div>
</div>
<div id="mobile-body">
<form id="form">
<div class="form-group">
<label for="name">Как к вам обращаться? (необязательно)</label>
<input type="text" id="name" placeholder="Например, Анна">
</div>
<div class="form-group">
<label for="question">Ваш вопрос:</label>
<textarea id="question" rows="3">__QUERY__</textarea>
</div>
<div class="btn-group">
<button type="button" id="askBtn">Спросить</button>
<button type="button" id="resetBtn" class="btn-secondary">Спросить ещё</button>
</div>
</form>
<div id="result" class="card visible">
<p>__ANSWER__</p>
</div>
<div class="footer">
<hr class="footer-divider">
<span>Есть идея или нашли ошибку?</span><br>
<a href="mailto:babushkaskazhet@example.com?subject=Обратная%20связь%20для%20БабушкаСкажет" class="feedback-btn">Написать бабушке</a>
</div>
</div>
</div>

<!-- ПК/планшетная версия -->
<div class="container">
<h1><span class="brand">БабушкаСкажет:</span> __QUERY__</h1>
<form id="form-pc">
<div class="form-group">
<label for="name-pc">Как к вам обращаться? (необязательно)</label>
<input type="text" id="name-pc" placeholder="Например, Анна">
</div>
<div class="form-group">
<label for="question-pc">Ваш вопрос:</label>
<textarea id="question-pc" rows="3">__QUERY__</textarea>
</div>
<div class="btn-group">
<button type="button" id="askBtn-pc">Спросить</button>
<button type="button" id="resetBtn-pc" class="btn-secondary">Спросить ещё</button>
</div>
</form>
<div id="result-pc" class="card visible">
<p>__ANSWER__</p>
</div>
<div class="footer">
<hr class="footer-divider">
<span>Есть идея или нашли ошибку?</span><br>
<a href="mailto:babushkaskazhet@example.com?subject=Обратная%20связь%20для%20БабушкаСкажет" class="feedback-btn">Написать бабушке</a>
</div>
</div>

<script src="/scripts/seo-app.js"></script>
</body>
</html>
'''

def read_answers(path):
    result = {}
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader, None)
        for row in reader:
            if row and len(row) >= 2:
                result[row[0].strip()] = row[1].strip()
    return result

def main():
    answers = read_answers(CSV_IN)
    with open(MAP_IN, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        entries = []
        for row in reader:
            if not row or len(row) < 4:
                continue
            new_url = row[3].strip()
            parts = new_url.strip('/').split('/')
            if len(parts) != 2:
                print(f'!! Некорректный new_url: {new_url}')
                continue
            entries.append({
                'query': row[0].strip(),
                'category': parts[0],
                'slug': parts[1],
                'answer': answers.get(row[0].strip(), ''),
            })

    created = 0
    empty = 0
    for e in entries:
        out_dir = os.path.join(PROJECT, e['category'], e['slug'])
        os.makedirs(out_dir, exist_ok=True)

        if not e['answer']:
            empty += 1

        title = f"{e['query']} | БабушкаСкажет"
        desc = f"Узнайте, что означает «{e['query']}». Тёплый ответ от бабушки."
        html = (TEMPLATE
            .replace('__TITLE__', title)
            .replace('__DESC__', desc)
            .replace('__METRIKA__', METRIKA)
            .replace('__QUERY__', e['query'])
            .replace('__ANSWER__', e['answer'])
        )
        with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html)
        created += 1

    print(f'Создано файлов: {created}')
    if empty:
        print(f'Внимание: без ответа {empty}')

if __name__ == '__main__':
    main()
