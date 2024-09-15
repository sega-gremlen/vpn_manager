from datetime import datetime

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column

from app.db.creator import Base


class Payments(Base):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey('subscriptions.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column()

    # Параметры api yoomoney
    notification_type: Mapped[str] = mapped_column()
    operation_id: Mapped[str] = mapped_column()
    operation_label: Mapped[str] = mapped_column()
    amount: Mapped[float] = mapped_column()
    withdraw_amount: Mapped[float] = mapped_column()
    currency: Mapped[int]
    api_datetime: Mapped[datetime] = mapped_column()
    sender: Mapped[str] = mapped_column()
    label: Mapped[str] = mapped_column(ForeignKey('payment_requests.label'))
    sha1_hash: Mapped[str] = mapped_column()
    unaccepted: Mapped[bool] = mapped_column()
