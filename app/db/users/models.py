from datetime import datetime

from sqlalchemy import UUID, Identity, BigInteger
from sqlalchemy.orm import Mapped, mapped_column


from app.db.creator import Base


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    telegram_id: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column()
    xray_uuid: Mapped[str | None] = mapped_column(UUID, nullable=True)

    def __str__(self):
        return ', '.join((str(self.telegram_id), str(self.created_at), str(self.xray_uuid)))
