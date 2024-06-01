from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


from app.db.creator import Base


class Periods(Base):
    __tablename__ = 'periods'

    id: Mapped[str] = mapped_column(primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey('subscriptions.id'))
    start: Mapped[date] = mapped_column()
    stop: Mapped[date] = mapped_column()

    def __str__(self):
        return ', '.join((str(self.id), str(self.subscription_id), str(self.start), str(self.stop)))
