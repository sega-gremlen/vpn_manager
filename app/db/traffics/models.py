from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, BigInteger


from app.db.creator import Base


class Traffics(Base):
    __tablename__ = 'traffics'

    id: Mapped[int] = mapped_column(primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey('periods.id'))
    created_at: Mapped[datetime] = mapped_column()
    downlink: Mapped[int] = mapped_column(BigInteger)
    uplink: Mapped[int] = mapped_column(BigInteger)

    def __str__(self):
        return f'{self.id}'

