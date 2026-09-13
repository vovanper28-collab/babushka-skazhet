// scripts/app.js
document.addEventListener('DOMContentLoaded', async function() {
  const isMobile = window.innerWidth <= 600;

  const nameInput = document.getElementById(isMobile ? 'name' : 'name-pc');
  const questionInput = document.getElementById(isMobile ? 'question' : 'question-pc');
  const askBtn = document.getElementById(isMobile ? 'askBtn' : 'askBtn-pc');
  const resetBtn = document.getElementById(isMobile ? 'resetBtn' : 'resetBtn-pc');
  const resultContainer = document.getElementById(isMobile ? 'result' : 'result-pc');
  const loadingEl = document.getElementById('loading');

  if (loadingEl) loadingEl.textContent = 'Бабушка готовится...';

  try {
    await DataManager.load();
    console.log('✅ Локальные данные загружены');
    if (loadingEl) loadingEl.textContent = '';
  } catch (error) {
    console.error('❌ Не удалось загрузить локальные данные:', error);
    if (loadingEl) loadingEl.textContent = 'Бабушке не здоровится, обратись позже';
  }

  if (!askBtn || !resultContainer) {
    console.error('❌ Кнопка или контейнер не найдены!');
    return;
  }

  askBtn.addEventListener('click', async function() {
    const userName = nameInput ? nameInput.value.trim() : '';
    const userQuestion = questionInput ? questionInput.value.trim() : '';

    if (userQuestion === '') {
      alert('Задай вопрос, внученька');
      return;
    }

    // Показываем индикатор загрузки
    resultContainer.innerHTML = `<div class="card visible"><p>Бабушка думает... ✍️</p></div>`;
    resultContainer.classList.add('visible');

    try {
      // Отправляем запрос на сервер
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userName, question: userQuestion }),
      });

      const data = await response.json();

      if (data.answer) {
        // ✅ Ответ от YandexGPT
        resultContainer.innerHTML = `
          <div class="card visible">
            <p class="full">${data.answer}</p>
          </div>
        `;
      } else {
        // Если ответа нет — используем локальную генерацию
        useLocalResponse(userName, userQuestion);
      }
    } catch (error) {
      console.error('Ошибка при вызове API:', error);
      useLocalResponse(userName, userQuestion);
    }

    // Функция локального ответа (fallback)
    function useLocalResponse(userName, userQuestion) {
      if (DataManager.get()) {
        const response = generateResponse(userName, userQuestion);
        if (response.isBlocked) {
          resultContainer.innerHTML = `<div class="card visible"><p>${response.full}</p></div>`;
          return;
        }
        resultContainer.innerHTML = `
          <div class="card visible">
            <p class="greeting">${response.greeting}</p>
            <p class="proverb">${response.proverb}</p>
            <p class="support">${response.support}</p>
            <hr>
            <p class="full">${response.full}</p>
          </div>
        `;
      } else {
        resultContainer.innerHTML = `<div class="card visible"><p>Бабушка не готова, попробуйте позже</p></div>`;
      }
    }
  });

  // Кнопка "Спросить ещё" — очищает поля и результат
  if (resetBtn) {
    resetBtn.addEventListener('click', function() {
      if (nameInput) nameInput.value = '';
      if (questionInput) questionInput.value = '';
      resultContainer.innerHTML = '';
      resultContainer.classList.remove('visible');
    });
  }
});