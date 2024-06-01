from datetime import datetime, date

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column


from app.db.creator import Base


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id'))
    subscription_type: Mapped[str] = mapped_column(ForeignKey('subscription_types.name'))
    created_at: Mapped[datetime] = mapped_column()
    start: Mapped[date] = mapped_column()
    stop: Mapped[date] = mapped_column()

    def __str__(self):
        return 'Подписка: ', ', '.join((str(self.id), str(self.created_at), str(self.start), str(self.stop)))
