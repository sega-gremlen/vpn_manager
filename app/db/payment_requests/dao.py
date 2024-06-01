import asyncio
import pprint

from app.db.payment_requests.models import PaymentRequests
# from app.db.subscribe_types.models import SubscriptionTypes
from app.db.dao.base import BaseDAO

from sqlalchemy import select
from app.db.creator import async_sessionmaker


class PaymentRequestsDAO(BaseDAO):
    model = PaymentRequests

    async def find_last_payment_request(self, user_id):
        async with async_sessionmaker() as session:
            querry = select(self.model).filter_by(user_id=user_id).order_by(self.model.created_at.desc())
            result = await session.execute(querry)
            return result.scalars().first()


if __name__ == '__main__':

    async def test():
        payment_request = await PaymentRequestsDAO().find_last_payment_request(7)
        print(payment_request)

    asyncio.run(test())
