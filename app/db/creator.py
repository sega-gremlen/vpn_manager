import asyncio
import asyncpg
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings


if settings.MODE == "TEST":
    DATABASE_PARAMS = {"poolclass": NullPool}
else:
    DATABASE_PARAMS = {}

engine = create_async_engine(settings.get_database_url(), **DATABASE_PARAMS)  #  echo=True)
async_sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def create_database(db_name):
    conn = await asyncpg.connect(
        user=settings.DB_USER,
        password=settings.DB_PASS,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database='postgres',
    )

    # Проверка наличия базы данных
    result = await conn.fetchrow("SELECT 1 FROM pg_database WHERE datname = $1", db_name)

    if not result:
        # Создание базы данных, если она отсутствует
        await conn.execute(f'CREATE DATABASE {db_name}')
        print(f"База данных {db_name} создана")
    else:
        print(f"База данных {db_name} уже существует")

    await conn.close()


# Запуск функции создания базы данных
if __name__ == '__main__':
    asyncio.run(create_database(settings.DB_NAME))
