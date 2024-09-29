Запуск проекта:


1. Настраиваем портал-сервер:
Отредактировать MAIN_HOST == NOTI_HOST == ip сервера
Добавляем .env
docker compose build && docker compose up panel
Меняем логин и пароль пользователя
docker compose bild && docker compose up
Проверяем что всё норм и запускаем в фоне
Меняем порт ssh
Добавить в настройки x-ui reverse прокси
Добавить настройки по гео
Поднять 3x-ui на евро сервере

2. Настраиваем бридж-сервер:
Копируем конфигурацию бриджа из портал-сервера.
Добавляем во outbounds конфигурацию
Добавляем реверс 

3. Поменять ip в уведомлениях на Юмоней: https://yoomoney.ru/transfer/myservices/http-notification?lang=ru

Порты:
1. Fastapi: 37777
2. Panel ui: 37778
3. Panel inbound: 37465
4. DB: 37779
5. SSH: 37780

Api ЮMoney: https://yoomoney.ru/docs/payment-buttons/using-api/flow