from typing import Literal
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        # env_file="/home/fila/PycharmProjects/vpn_manager/.env",
        env_prefix="TEST_" if os.getenv("MODE") == 'TEST' else "",
        case_sensitive=False,
        extra='ignore',
    )

    MODE: Literal["DEV", "TEST", "PROD"]
    MAIN_HOST: str

    # ------------ БД
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    def get_database_url(self, sync=False):
        url_begin = 'postgresql+asyncpg' if not sync else 'postgresql'
        return (
            f'{url_begin}://{self.DB_USER}:'
            f'{self.DB_PASS}@'
            f'{self.DB_HOST}:'
            f'{self.DB_PORT}/'
            f'{self.DB_NAME}'
        )

    # ------------ Бот
    BOT_TOKEN: str
    ADMIN_ID: int
    BOT_ID: int
    BOT_TEMPLATES_PATH: str = str(os.path.join(os.path.dirname(__file__), 'app/bot/utils'))
    SUPPORT_ID: str

    # ------------ Подписки
    TRAFFIC_LIMIT: int  # Лимит на одного клиента, Гб.
    @property
    def sub_plan(self):
        return [
            {'name': 'type_1', 'price': 80, 'duration': 30},
            {'name': 'type_6', 'price': 400, 'duration': 180},
            {'name': 'type_12', 'price': 600, 'duration': 360},
            {'name': 'trial', 'price': 0, 'duration': 14},
        ]

    # ------------ 3x-ui
    PANEL_HOST: str
    PANEL_PORT: str
    PANEL_USERNAME: str
    PANEL_PASSWORD: str
    PUBKEY: str
    PRVTKEY: str
    MASK_HOST: str
    SID: str
    INBOUND_ID: int
    INBOUND_PORT: int
    PROFILE_NAME: str
    BRIDGE_UUID: str

    # ------------ Уведомления
    NOTI_SECRET: str  # Секретный код для проверки хэш суммы уведомления
    RECIEVER: int
    NOTI_HOST: str  # Хост fastapi для получения уведомлений
    NOTI_PORT: int  # Порт fastapi для получения уведомлений
    REDIRECT_URL_LIVING_TIME: int  # Время жизни редирект-ссылки на оплату, с.
    API_TEMPLATES_PATH: str = str(os.path.join(os.path.dirname(__file__), 'app/static/api_templates'))

settings = Settings()
