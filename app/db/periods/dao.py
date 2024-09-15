from datetime import datetime

from sqlalchemy import select

from app.db.periods.models import Periods
from app.db.subscriptions.models import Subscriptions
from app.db.dao.base import BaseDAO
from app.db.creator import async_sessionmaker
from app.db.users.models import Users


class PeriodsDAO(BaseDAO):
    model = Periods

    @staticmethod
    async def find_current_period_sub(telegram_id):
        async with async_sessionmaker() as session:
            dt_now = datetime.now()

            query = (
                select(Periods.__table__.columns,
                       Subscriptions.__table__.columns)
                .join(Subscriptions, Periods.subscription_id == Subscriptions.id)  # Сначала соединяем с Subscriptions
                .join(Users, Subscriptions.user_id == Users.id)  # Затем соединяем с Users
                .filter(
                    Users.telegram_id == telegram_id,
                    Periods.start <= dt_now,
                    Periods.stop >= dt_now
                )
            )

            result = await session.execute(query)
            return result.mappings().first()
