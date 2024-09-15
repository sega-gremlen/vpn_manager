from sqlalchemy import select

from app.db.payment_requests.models import PaymentRequests
from app.db.dao.base import BaseDAO
from app.db.creator import async_sessionmaker


class PaymentRequestsDAO(BaseDAO):
    model = PaymentRequests

    async def find_last_payment_request(self, user_id):
        async with async_sessionmaker() as session:
            querry = select(self.model).filter_by(user_id=user_id).order_by(self.model.created_at.desc())
            result = await session.execute(querry)
            return result.scalars().first()
