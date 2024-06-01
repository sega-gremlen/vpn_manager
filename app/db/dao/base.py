import pprint

from app.db.creator import async_sessionmaker

from sqlalchemy import select, insert


class BaseDAO:
    model = None

    @classmethod
    async def find_first_by_filter(cls, **filter_by):
        async with async_sessionmaker() as session:
            querry = select(cls.model).filter_by(**filter_by)
            result = await session.execute(querry)
            return result.scalars().first()

    @classmethod
    async def find_all_by_filter(cls, **filter_by):
        async with async_sessionmaker() as session:
            querry = select(cls.model).filter_by(**filter_by)
            result = await session.execute(querry)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_sessionmaker() as session:
            querry = select(cls.model).filter_by(**filter_by)
            result = await session.execute(querry)
            return result.scalar_one_or_none()

    @classmethod
    async def create(cls, **data):
        async with async_sessionmaker() as session:
            querry = insert(cls.model).values(**data).returning(cls.model)
            result = await session.execute(querry)
            await session.commit()
            return result.scalar()

    @classmethod
    async def patch_some(cls, model_obj, **data):
        async with async_sessionmaker() as session:
            for key, value in data.items():
                setattr(model_obj, key, value)

            session.add(model_obj)
            await session.commit()




