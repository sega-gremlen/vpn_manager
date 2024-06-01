from datetime import date

from app.db.subscriptions.models import Subscriptions
from app.db.dao.base import BaseDAO

from sqlalchemy import select
from app.db.creator import async_sessionmaker


class SubscriptionsDAO(BaseDAO):
    model = Subscriptions

    async def find_last_subscription(self, user_id):
        async with async_sessionmaker() as session:
            querry = session.query(self.model).filter_by(user_id=user_id).all()
            result = await session.execute(querry)
            return result.scalar_one_or_none()

    # async def find_current_subscription(self, user_id):
    #     async with async_sessionmaker() as session:
    #
    #         subscription = select(self.model).filter(
    #             date.today() <= self.model.stop,
    #             date.today() >= self.model.start,
    #             Subscriptions.user_id == user_id,
    #         )
    #         subscription = await session.execute(subscription)
    #         return subscription.scalars()


if __name__ == '__main__':
    import asyncio
    asyncio.run(SubscriptionsDAO().find_current_subscription(1))
