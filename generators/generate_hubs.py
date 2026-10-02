#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv, os, html

PROJECT = '/var/www/babushka-skazhet'
MAP_IN  = os.path.join(PROJECT, 'url-migration/url-map.csv')

CATEGORIES = {
    'primety':     ('Приметы', 'Народные приметы на все случаи жизни: что означает чешется ладонь, разбилось зеркало, встретил чёрную кошку.'),
    'sny':         ('Сны', 'Толкование снов: что значит, если снится вода, покойник, змея, деньги или свадьба.'),
    'otnosheniya': ('Отношения и семья', 'Советы про любовь, семью, детей, ссоры и примирение — от лица доброй бабушки.'),
    'dengi':       ('Деньги и достаток', 'Приметы и советы про деньги, богатство, прибыль, долги и финансовое благополучие.'),
    'zdorove':     ('Здоровье', 'Народные советы про здоровье: бессонница, головная боль, простуда, иммунитет.'),
    'sovety':      ('Советы на каждый день', 'Мудрые житейские советы бабушки: как найти себя, быть счастливой, наладить жизнь.'),
}

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

# ВАЖНО: body class="hub-page" вместо "seo-page"
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
<body class="hub-page">

<div class="container">
<h1><span class="brand">БабушкаСкажет:</span> __CAT_TITLE__</h1>
<p class="hub-intro">__CAT_DESC__</p>

<div class="hub-list">
__LINKS__
</div>

<div class="footer">
<hr class="footer-divider">
<span>Есть идея или нашли ошибку?</span><br>
<a href="mailto:babushkaskazhet@example.com?subject=Обратная%20связь%20для%20БабушкаСкажет" class="feedback-btn">Написать бабушке</a>
</div>
</div>

</body>
</html>
'''

def main():
    by_cat = {c: [] for c in CATEGORIES}
    with open(MAP_IN, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        for row in reader:
            if len(row) < 4: continue
            url = row[3].strip().strip('/')
            parts = url.split('/')
            if len(parts) != 2: continue
            cat, slug = parts
            if cat in by_cat:
                by_cat[cat].append({'query': row[0].strip(), 'slug': slug})

    created = 0
    for cat, items in by_cat.items():
        cat_title, cat_desc = CATEGORIES[cat]
        items.sort(key=lambda x: x['query'].lower())

        links = []
        for it in items:
            q = html.escape(it['query'])
            links.append(f'<a href="/{cat}/{it["slug"]}/" class="hub-link">{q}</a>')

        title = f'{cat_title} | БабушкаСкажет'
        page_html = (TEMPLATE
            .replace('__TITLE__', title)
            .replace('__DESC__', html.escape(cat_desc))
            .replace('__METRIKA__', METRIKA)
            .replace('__CAT_TITLE__', html.escape(cat_title))
            .replace('__CAT_DESC__', html.escape(cat_desc))
            .replace('__LINKS__', '\n'.join(links))
        )

        with open(os.path.join(PROJECT, cat, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(page_html)
        created += 1

    print(f'Пересоздано хаб-страниц: {created}')

if __name__ == '__main__':
    main()
