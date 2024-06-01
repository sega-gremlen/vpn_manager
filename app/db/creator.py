import asyncio

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Постоянные БД
DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'postgres'
DB_PASS = 'postgres'
DB_NAME = 'vpn_manager'

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_async_engine(DATABASE_URL) #  echo=True)
async_sessionmaker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def create_database():
    conn = await asyncpg.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, database='postgres')

    # Проверка наличия базы данных
    result = await conn.fetchrow("SELECT 1 FROM pg_database WHERE datname = $1", DB_NAME)

    if not result:
        # Создание базы данных, если она отсутствует
        await conn.execute(f'CREATE DATABASE {DB_NAME}')
        print(f"Database {DB_NAME} created successfully.")
    else:
        print(f"Database {DB_NAME} already exists.")

    await conn.close()


# Запуск функции создания базы данных
if __name__ == '__main__':
    asyncio.run(create_database())
