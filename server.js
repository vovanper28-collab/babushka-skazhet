// server.js (финальная версия с подробным логированием)
const express = require('express');
const cors = require('cors');
const path = require('path');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Проверка переменных окружения
console.log('🔑 Проверка переменных окружения:');
console.log('   YANDEX_API_KEY:', process.env.YANDEX_API_KEY ? '✅ задан (первые 10 символов: ' + process.env.YANDEX_API_KEY.substring(0, 10) + '...)' : '❌ не задан');
console.log('   YANDEX_FOLDER_ID:', process.env.YANDEX_FOLDER_ID ? '✅ задан (' + process.env.YANDEX_FOLDER_ID + ')' : '❌ не задан');

if (!process.env.YANDEX_API_KEY || !process.env.YANDEX_FOLDER_ID) {
  console.error('❌ Ошибка: не заданы YANDEX_API_KEY или YANDEX_FOLDER_ID в файле .env');
  process.exit(1);
}

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname)));

app.post('/api/generate', async (req, res) => {
  const { userName, question } = req.body;

  if (!question || question.trim() === '') {
    return res.status(400).json({ error: 'Вопрос не может быть пустым' });
  }

  const prompt = `
Ты — добрая русская бабушка. Отвечай на вопросы внуков тепло, с любовью и мудростью.
Обязательно используй русские пословицы и поговорки в своём ответе.
Говори от первого лица, обращайся к спрашивающему ласково.

Вопрос: "${question}"
Обращение: ${userName || 'внученька'}

Ответ бабушки:
`;

  console.log(`📩 Запрос от ${userName || 'анонима'}: ${question}`);

  try {
    // Формируем тело запроса к YandexGPT
    const requestBody = {
      modelUri: `gpt://${process.env.YANDEX_FOLDER_ID}/yandexgpt-lite`,
      completionOptions: {
        temperature: 0.8,
        maxTokens: 500,
      },
      messages: [
        {
          role: 'system',
          text: 'Ты — добрая русская бабушка. Отвечай на вопросы внуков тепло, с любовью и мудростью. Используй русские пословицы и поговорки. Говори от первого лица, обращайся к спрашивающему ласково.'
        },
        {
          role: 'user',
          text: prompt
        }
      ]
    };

    console.log('📤 Отправка запроса к YandexGPT...');
    console.log('   modelUri:', requestBody.modelUri);

    const response = await fetch('https://llm.api.cloud.yandex.net/foundationModels/v1/completion', {
      method: 'POST',
      headers: {
        'Authorization': `Api-Key ${process.env.YANDEX_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    console.log('📥 Статус ответа YandexGPT:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Текст ошибки от YandexGPT:', errorText);
      throw new Error(`YandexGPT вернул ошибку ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('✅ YandexGPT ответ получен');

    // Проверяем структуру ответа
    if (data.result && data.result.alternatives && data.result.alternatives[0]) {
      const answer = data.result.alternatives[0].message.text;
      console.log('   Ответ:', answer.substring(0, 50) + '...');
      res.status(200).json({ answer });
    } else {
      console.error('❌ Неожиданный формат ответа:', JSON.stringify(data, null, 2));
      throw new Error('Неверная структура ответа от YandexGPT');
    }

  } catch (error) {
    console.error('❌ Ошибка при вызове YandexGPT:', error.message);
    res.status(500).json({
      answer: 'Ой, внученька, что-то я притомилась. Попробуй ещё разок, а я пока чайку попью. 🙏'
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Сервер запущен на http://localhost:${PORT}`);
});