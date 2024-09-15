from datetime import datetime

from sqlalchemy import ForeignKey, Identity, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.creator import Base


class Periods(Base):
    __tablename__ = 'periods'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey('subscriptions.id'))
    # Текущий период включает дни, которые => start-день, всё что меньше этого дня предыдущий период
    start: Mapped[datetime] = mapped_column()
    # Текущий период включает дни, которые <= stop-день, всё что больше этого дня другой следующий период
    stop: Mapped[datetime] = mapped_column()
    current_value: Mapped[int] = mapped_column(BIGINT, default=0)

    def __str__(self):
        return ', '.join((str(self.id), str(self.subscription_id), str(self.start), str(self.stop)))



