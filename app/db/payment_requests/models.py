from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Identity, ForeignKey, BigInteger

from app.db.creator import Base



class PaymentRequests(Base):
    __tablename__ = 'payment_requests'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    label: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column()
    stop_at: Mapped[datetime] = mapped_column()
    periods: Mapped[int] = mapped_column()
    subscription_type_id: Mapped[int] = mapped_column(ForeignKey('subscription_types.id'))
    completed: Mapped[bool] = mapped_column(default=False)
    redirect_url: Mapped[str] = mapped_column()

    def __str__(self):
        return repr(self.__dict__)
