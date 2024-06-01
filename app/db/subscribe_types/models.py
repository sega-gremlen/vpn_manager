from sqlalchemy.orm import Mapped, mapped_column


from app.db.creator import Base


class SubscriptionTypes(Base):
    __tablename__ = 'subscription_types'

    name: Mapped[str] = mapped_column(primary_key=True)
    price: Mapped[int] = mapped_column()
