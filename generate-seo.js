const fs = require('fs');
const path = require('path');

// Читаем CSV
const csvFile = 'table.csv';
const csvContent = fs.readFileSync(csvFile, 'utf8');
const lines = csvContent.split('\n').filter(line => line.trim() !== '');

const rows = lines.map(line => {
  const parts = line.split(';');
  if (parts.length < 2) return null;
  return { query: parts[0].trim(), answer: parts[1].trim() };
}).filter(row => row !== null);

const outputDir = 'seo';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir);
}

// Транслитерация
function transliterate(word) {
  const map = {
    'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
    'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m',
    'н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u',
    'ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch',
    'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
  };
  let result = '';
  for (let ch of word.toLowerCase()) {
    result += map[ch] || ch;
  }
  return result.replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

// Генерация
rows.forEach(row => {
  const query = row.query;
  const answer = row.answer;
  const urlPart = transliterate(query);
  const fileName = `${urlPart}.html`;
  const filePath = path.join(outputDir, fileName);

  const title = `${query} | БабушкаСкажет`;
  const description = `Узнайте, что означает «${query}». Тёплый ответ от бабушки.`;

  const html = `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <meta name="description" content="${description}">
  <link rel="stylesheet" href="/styles/style.css">
</head>
<body>
  <div class="container">
    <h1>${query}</h1>
    <div id="result" class="card visible">
      <p>${answer}</p>
    </div>
    <button id="anotherBtn" style="margin-top:1rem; background:#d4a88c; color:#3e2c1b; border-radius:40px; padding:0.7rem 1.2rem; border:none; font-size:1rem; cursor:pointer;">Спросить по-другому</button>
    <div style="margin-top:2rem;">
      <h2 style="font-size:1.2rem; font-family:Georgia;">Задайте свой вопрос</h2>
      <form id="askForm">
        <div class="form-group">
          <label for="name">Как к вам обращаться? (необязательно)</label>
          <input type="text" id="name" placeholder="Например, Анна">
        </div>
        <div class="form-group">
          <label for="question">Ваш вопрос:</label>
          <textarea id="question" rows="3" placeholder="О чём хотите спросить?"></textarea>
        </div>
        <div class="btn-group">
          <button type="button" id="askBtn">Спросить</button>
          <button type="button" id="resetBtn" class="btn-secondary">Спросить ещё</button>
        </div>
      </form>
    </div>
    <div id="resultDynamic" class="card"></div>
  </div>

  <div class="footer">
    <span>Есть идея или нашли ошибку?</span><br>
    <a href="mailto:babushkaskazhet@example.com?subject=Обратная%20связь%20для%20БабушкаСкажет" class="feedback-btn">📩 Написать бабушке</a>
  </div>

  <script src="/scripts/dataManager.js"></script>
  <script src="/scripts/generator.js"></script>
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      (function() {
        var nameInput = document.getElementById('name');
        var questionInput = document.getElementById('question');
        var askBtn = document.getElementById('askBtn');
        var resetBtn = document.getElementById('resetBtn');
        var resultContainer = document.getElementById('resultDynamic');
        if (!askBtn) return;
        askBtn.addEventListener('click', function() {
          var userName = nameInput ? nameInput.value : '';
          var userQuestion = questionInput ? questionInput.value.trim() : '';
          if (userQuestion === '') { alert('Задай вопрос, внученька'); return; }
          var response = generateResponse(userName, userQuestion);
          if (response.isBlocked) {
            resultContainer.innerHTML = '<div class="card"><p>' + response.full + '</p></div>';
            resultContainer.classList.add('visible');
            return;
          }
          resultContainer.innerHTML = '<div class="card">' +
            '<p class="greeting">' + response.greeting + '</p>' +
            '<p class="proverb">' + response.proverb + '</p>' +
            '<p class="support">' + response.support + '</p>' +
            '<hr>' +
            '<p class="full">' + response.full + '</p>' +
            '</div>';
          resultContainer.classList.add('visible');
        });
        if (resetBtn) {
          resetBtn.addEventListener('click', function() {
            if (nameInput) nameInput.value = '';
            if (questionInput) questionInput.value = '';
            resultContainer.innerHTML = '';
            resultContainer.classList.remove('visible');
          });
        }
        DataManager.load().then(function() {
          console.log('✅ Данные загружены');
        }).catch(function(err) {
          console.error('Ошибка загрузки данных:', err);
        });
      })();
    });
    document.getElementById('anotherBtn').addEventListener('click', function() {
      var h1 = document.querySelector('h1');
      var questionText = h1 ? h1.textContent : '';
      var response = generateResponse('', questionText);
      var card = document.getElementById('result');
      if (card && response.full) {
        card.innerHTML = '<p>' + response.full + '</p>';
      }
    });
  </script>
</body>
</html>`;

  fs.writeFileSync(filePath, html, 'utf8');
  console.log('Создана: ' + filePath);
});

console.log('✅ Готово! Все страницы созданы в папке seo/');