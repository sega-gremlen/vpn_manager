Для деплоя:
1. Отредактировать MAIN_HOST == NOTI_HOST == ip сервера
2. Поменять ip в уведомлениях на Юмоней: https://yoomoney.ru/transfer/myservices/http-notification?lang=ru
3. Добавить в настройки x-ui reverse прокси
4. Добавить настройки по гео
5. Поднять 3x-ui на евро сервере

Порты:
1. Fastapi: 37777
2. Panel ui: 37778
3. Panel inbound: 37465
4. DB: 37779
5. SSH: 37780