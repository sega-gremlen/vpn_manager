from app.db.periods.models import Periods
from app.db.subscriptions.models import Subscriptions
from app.db.dao.base import BaseDAO

from app.db.creator import async_sessionmaker


class PeriodsDAO(BaseDAO):
    model = Periods

    async def find_current_period(self, user_id):
        async with async_sessionmaker() as session:
            subscription = select(self.model).filter(
                date.today() <= self.model.stop,
                date.today() >= self.model.start,
                Subscriptions.user_id == user_id,
            )


            subscription = await session.execute(subscription)
            return subscription.scalars()
