<h1>Бот предназаначен для обработки изображений</h1>
<h2>Исходное фото:</h2>
<p><img src="https://github.com/user-attachments/assets/6cbc1e08-d10f-49e7-be76-346b6145c31d" width="50%" height="50%"></p>
<h2>Результат:</h2>
<p><img src="https://github.com/user-attachments/assets/59249c59-0383-4b81-a90e-fa410af4f8fe" width="50%" height="50%"></p>

<ol>Использование:
  <li>Загрузи фото</li>
  <li>Выбери тип карточки</li>
  <li>Придумай подпись</li>
  <li>Получи результат</li>
</ol>

<h2>Настройки</h2>
<p>Перейдите в файл .env и укажите свои данные

<h4>- Настройки бота:</h4>
  <p>TOKEN = 'токен вашего бота'</p>
  <p>ADMIN = ['user_id админ аккаунта',]</p>
<h4>- Настройки БД:</h4>
  <p>HOST = "хост сервера"</p>
  <p>DB_NAME = "Название БД"</p>
  <p>USER =  "пользователь"</p>
  <p>PASSWORD = "пароль"</p>
  <p>PORT =  "порт" (по умолчанию 5432)</p>

<p>
<ul>Используемые библиотеки:
  <li>Телеграм бот - aiogram 2.5.1</li>
  <li>Обработка изображений - pillow</li>
  <li>БД - postrgesql</li>
  <li>Orm - sqlalchemy</li>
  <li>Миграции - alembic</li>
</ul>
</p>
