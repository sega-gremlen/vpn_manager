import pprint

from aiohttp.web_routedef import delete

from app.db.creator import async_sessionmaker

from sqlalchemy import select, insert, desc, delete


class BaseDAO:
    model = None

    @classmethod
    async def find_first_by_filter(cls, **filter_by):
        async with async_sessionmaker() as session:
            querry = select(cls.model).filter_by(**filter_by)
            result = await session.execute(querry)
            return result.scalars().first()

    @classmethod
    async def find_last_by_filter(cls, order_by, **filter_by):
        async with async_sessionmaker() as session:
            query = select(cls.model).filter_by(**filter_by).order_by(desc(getattr(cls.model, order_by)))
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_all_by_filter(cls, *filter_by):
        async with async_sessionmaker() as session:
            querry = select(cls.model.__table__.columns).filter(*filter_by)
            result = await session.execute(querry)
            return result.mappings().all()

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
    async def delete_all_by_filter(cls, *filter_by):
        async with async_sessionmaker() as session:
            await session.execute(delete(cls.model).filter(*filter_by))
            await session.commit()


    @staticmethod
    async def patch(model_obj, **data):
        async with async_sessionmaker() as session:
            for key, value in data.items():
                setattr(model_obj, key, value)

            session.add(model_obj)
            await session.commit()

    @classmethod
    async def join_request(cls, right_table, *filter_by):
        async with async_sessionmaker() as session:
            querry = select(cls.model.__table__.columns,
                            right_table.__table__.columns).join(cls.model).filter(*filter_by)
            result = await session.execute(querry)
            return result.mappings().first()
