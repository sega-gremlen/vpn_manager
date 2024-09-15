from datetime import datetime

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column

from app.db.creator import Base


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    subscription_type_id: Mapped[str] = mapped_column(ForeignKey('subscription_types.id'))
    # Подписка действует с момента времени в который пришли деньги
    start: Mapped[datetime] = mapped_column()
    # Подписка заканчивается в день который > stop-день
    stop: Mapped[datetime] = mapped_column()

    def __str__(self):
        return 'Подписка: ' + ', '.join((str(self.id), str(self.start), str(self.stop)))
