from datetime import datetime

from sqlalchemy import select

from app.db.periods.models import Periods
from app.db.subscriptions.models import Subscriptions
from app.db.users.models import Users
from app.db.creator import async_sessionmaker
from app.db.dao.base import BaseDAO


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def get_users_with_active_sub(cls):
        async with async_sessionmaker() as session:
            dt_now= datetime.now()

            query = (
                select(Users.__table__.columns,
                       Subscriptions.__table__.columns,
                       Periods.__table__.columns)
                .join(Subscriptions, Users.id == Subscriptions.user_id)
                .join(Periods, Subscriptions.id == Periods.subscription_id)
                .filter(
                    # Subscriptions.start <= dt_now,
                    # Subscriptions.stop >= dt_now,
                    Periods.start <= dt_now,
                    Periods.stop >= dt_now
                )
            )

            result = await session.execute(query)
            return result.mappings().all()




