from sqlalchemy import select, desc, insert

from app.db.subscription_types.models import SubscriptionTypes
from app.db.dao.base import BaseDAO
from app.db.creator import async_sessionmaker
from config import settings


class SubscriptionTypesDAO(BaseDAO):
    model = SubscriptionTypes

    @classmethod
    async def fill_subscription_types(cls):
        async with async_sessionmaker() as session:
            for item in settings.sub_plan:
                new_entry = insert(cls.model).values(**item)
                await session.execute(new_entry)
            await session.commit()

    async def get_actual_prices(self):
        async with async_sessionmaker() as session:
            sub_names = ('type_1', 'type_6', 'type_12')
            querries = [select(self.model).filter_by(name=i).order_by(desc(self.model.add_date)) for i in sub_names]
            result = [await session.execute(i) for i in querries]
            result = [i.scalars().first().price for i in result]
            result = dict(zip(sub_names, result))
            return result

    # async def get_actual_prices(self):
    #     async with async_sessionmaker() as session:
    #         sub_names = ('type_1', 'type_6', 'type_12')
    #         querries = [select(self.model).filter_by(name=i).order_by(desc(self.model.add_date)) for i in sub_names]
    #         result = [await session.execute(i) for i in querries]
    #         result = [i.scalars().first().price for i in result]
    #         result = dict(zip(sub_names, result))
    #         return result

