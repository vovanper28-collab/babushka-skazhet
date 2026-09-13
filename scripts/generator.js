// Функция проверки запрещённых запросов
function isForbidden(question, forbiddenData) {
  const lower = question.toLowerCase();
  const { words, phrases } = forbiddenData;

  for (let word of words) {
    if (lower.includes(word)) return true;
  }
  for (let phrase of phrases) {
    if (lower.includes(phrase)) return true;
  }
  return false;
}

// Основная функция генерации ответа
function generateResponse(userName, userQuestion) {
  const data = DataManager.get();
  if (!data) {
    return {
      isBlocked: false,
      full: 'Бабушка не готова, попробуйте позже'
    };
  }

  // Проверка на запрещённый контент
  if (isForbidden(userQuestion, data.forbidden)) {
    return {
      isBlocked: true,
      full: 'Родная моя, бабушка не может говорить на такие темы. Давай лучше спросим о чём-то, что принесет тебе свет и радость. Я верю, у тебя всё будет хорошо.'
    };
  }

  // 1. Определяем тональность вопроса
  const question = userQuestion.toLowerCase();
  let tonality = 'neutral';

  const negativeMarkers = ['стоит ли', 'рискнуть', 'боюсь', 'волнуюсь', 'страшно', 'сомневаюсь', 'переживаю', 'опасаюсь'];
  const positiveMarkers = ['удастся ли', 'получится ли', 'хочу', 'мечтаю', 'надеюсь'];

  for (let marker of negativeMarkers) {
    if (question.includes(marker)) {
      tonality = 'negative';
      break;
    }
  }
  if (tonality === 'neutral') {
    for (let marker of positiveMarkers) {
      if (question.includes(marker)) {
        tonality = 'positive';
        break;
      }
    }
  }

  // 2. Выбираем обращение
  let greeting;
  if (userName && userName.trim() !== '') {
    greeting = userName.trim();
  } else {
    const greetings = data.greetings;
    greeting = greetings[Math.floor(Math.random() * greetings.length)];
  }

  // 3. Выбираем присказку (по тональности)
  const proverbs = data.proverbs[tonality];
  const proverb = proverbs[Math.floor(Math.random() * proverbs.length)];

  // 4. Выбираем поддержку (по тональности)
  const supports = data.supports[tonality];
  const support = supports[Math.floor(Math.random() * supports.length)];

  // 5. Выбираем связки
  const beforeProverb = data.connectors.beforeProverb;
  const beforeSupport = data.connectors.beforeSupport;
  const connector1 = beforeProverb[Math.floor(Math.random() * beforeProverb.length)];
  const connector2 = beforeSupport[Math.floor(Math.random() * beforeSupport.length)];

  // 6. Склеиваем ответ
  const full = `${greeting}, ${connector1}: ${proverb}. ${connector2}: ${support}.`;

  // 7. Возвращаем результат
  return {
    isBlocked: false,
    greeting: greeting,
    proverb: proverb,
    support: support,
    full: full
  };
}