#!/bin/bash

# Проверка доступности порта панели
while ! (echo > /dev/tcp/"${PANEL_HOST}"/"${PANEL_PORT}") &> /dev/null; do
  echo "Waiting for ${PANEL_HOST}:${PANEL_PORT} to be ready..."
  sleep 1
done

# Активируем окружение
source /vpn_manager/venv/bin/activate

# Заполняем бд
python /vpn_manager/app/db/creator.py
alembic upgrade head

# Добавляем подключение
python /vpn_manager/app/panel_3x_ui_api.py

# Запускаем aps и бота
python /vpn_manager/app/start.py

# Запускаем fastapi
#gunicorn app.notification_api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --log-level debug --access-logfile - --error-logfile - &
#uvicorn app.notification_api:app --host 0.0.0.0 --port 8000 --log-level debug &


# Пробегаем тестами
# pytest

