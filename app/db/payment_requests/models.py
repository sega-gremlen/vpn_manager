from datetime import datetime, date
from pprint import pprint

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, Column, Identity, ForeignKey


from app.db.creator import Base
from app.db.subscribe_types.models import SubscriptionTypes
from app.db.users.models import Users


class PaymentRequests(Base):
    __tablename__ = 'payment_requests'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    telegram_id: Mapped[str] = mapped_column()
    label: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    stop_at: Mapped[datetime] = mapped_column()
    periods: Mapped[int] = mapped_column()
    subscription_type: Mapped[str] = mapped_column(ForeignKey('subscription_types.name'))
    completed: Mapped[bool] = mapped_column(default=False)
    redirect_url: Mapped[str] = mapped_column()

    def __str__(self):
        return repr(self.__dict__)
