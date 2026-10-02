// scripts/seo-app.js — форма на SEO-страницах (мобильная + ПК версии)
document.addEventListener('DOMContentLoaded', function () {
  var isMobile = window.innerWidth <= 600;

  var nameInput = document.getElementById(isMobile ? 'name' : 'name-pc');
  var questionInput = document.getElementById(isMobile ? 'question' : 'question-pc');
  var askBtn = document.getElementById(isMobile ? 'askBtn' : 'askBtn-pc');
  var resetBtn = document.getElementById(isMobile ? 'resetBtn' : 'resetBtn-pc');
  var resultContainer = document.getElementById(isMobile ? 'result' : 'result-pc');

  console.log('SEO-app loaded. isMobile:', isMobile, 'resultContainer:', resultContainer);

  if (!askBtn || !resultContainer) {
    console.error('SEO-app: не найдены элементы формы. askBtn:', askBtn, 'result:', resultContainer);
    return;
  }

  function sendQuestion(userName, userQuestion) {
    resultContainer.innerHTML = '<p>Бабушка думает... ✍️</p>';
    resultContainer.classList.add('visible');

    fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userName: userName, question: userQuestion })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
      if (data.answer) {
        resultContainer.innerHTML = '<p>' + data.answer + '</p>';
      } else {
        resultContainer.innerHTML = '<p>Бабушка не готова, попробуйте позже</p>';
      }
    })
    .catch(function (err) {
      console.error('Ошибка API:', err);
      resultContainer.innerHTML = '<p>Ой, внученька, что-то я притомилась. Попробуй ещё разок.</p>';
    });
  }

  askBtn.addEventListener('click', function () {
    var userName = nameInput ? nameInput.value.trim() : '';
    var userQuestion = questionInput ? questionInput.value.trim() : '';
    console.log('Ask clicked. Question:', userQuestion);
    if (userQuestion === '') { alert('Задай вопрос, внученька'); return; }
    sendQuestion(userName, userQuestion);
  });

  if (resetBtn) {
    resetBtn.addEventListener('click', function () {
      if (nameInput) nameInput.value = '';
      if (questionInput) questionInput.value = '';
      if (resultContainer) {
        resultContainer.innerHTML = '';
        resultContainer.classList.remove('visible');
      }
      if (questionInput) questionInput.focus();
    });
  }
});
