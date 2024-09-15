from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Identity


from app.db.creator import Base


class SubscriptionTypes(Base):
    __tablename__ = 'subscription_types'

    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column()
    price: Mapped[int] = mapped_column()
    duration: Mapped[int] = mapped_column()
