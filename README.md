Запуск проекта

Настраиваем портал-сервер:
- Отредактировать MAIN_HOST == NOTI_HOST == ip сервера
- Добавляем .env
- ```docker compose build && docker compose up panel```
- Меняем логин и пароль пользователя
- ```docker compose bild && docker compose up```
- Проверяем что всё норм и запускаем в фоне
- Добавить в настройки x-ui reverse прокси
- Добавить настройки по гео
- Поднять 3x-ui на евро сервере

Настраиваем бридж-сервер:
- Копируем конфигурацию бриджа из портал-сервера.
- Добавляем во outbounds конфигурацию
- Добавляем реверс 

Поменять ip в уведомлениях на Юмоней:
- https://yoomoney.ru/transfer/myservices/http-notification?lang=ru

Порты:
- Fastapi: 37777
- Panel ui: 37778
-  Panel inbound: 37465
-  DB: 37779
-  SSH: 37780

Api ЮMoney: https://yoomoney.ru/docs/payment-buttons/using-api/flow
