from sqlalchemy import select, desc

from app.db.subscriptions.models import Subscriptions
from app.db.dao.base import BaseDAO
from app.db.creator import async_sessionmaker
from app.db.users.models import Users


class SubscriptionsDAO(BaseDAO):
    model = Subscriptions

    @classmethod
    async def find_last_subscription_by_user_id(cls, user_id):
        """ Найти последнюю подписку по бд-id пользователя """

        async with async_sessionmaker() as session:
            query = select(cls.model).filter_by(user_id=user_id).order_by(desc(cls.model.id))
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_last_sub_by_user_tg_id(cls, tg_id):
        """ Найти последнюю подписку по tg-id пользователя """

        async with async_sessionmaker() as session:
            query = select(cls.model).join(
                Users, Users.id == cls.model.user_id
            ).filter(Users.telegram_id==tg_id).order_by(cls.model.id.desc())
            result = await session.execute(query)
            if result:
                return result.scalars().first()
            else:
                return None
