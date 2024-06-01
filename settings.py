from dataclasses import dataclass

from environs import Env

env = Env()
env.read_env()

MY_HOSTING = 'http://2.tcp.eu.ngrok.io:12446'
REDIRECT_URL_LIVING_TIME = 300  # Время жизни редирект-ссылки на оплату


@dataclass
class Bot:
    BOT_TOKEN: str
    ADMIN_ID: int
    BOT_ID: int


@dataclass
class DB:
    ...


@dataclass(frozen=True, slots=True)
class Settings:
    db_url: str = env.str(
        'DATABASE_URL',
        'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres',
    )
    BOT_TOKEN: str = env.str('BOT_TOKEN')
    ADMIN_ID: int = env.int('ADMIN_ID')
    BOT_ID: int = env.int('BOT_ID')


settings = Settings()
