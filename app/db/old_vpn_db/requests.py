import os.path
from typing import Tuple, Sequence, List

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Date,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from datetime import date

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'wiregram.db')


class Base(DeclarativeBase):
    pass


engine = create_engine(f"sqlite:///{DB_PATH}")

'''
Статусы подписок:
VIP - бессрочная
simple - обычная, срок окончания в столбце subscribe_duration, дата активации в столбце activated_date
expired - отсановленная по расписанию (чек раз в день), коментится в conf-файле WG, можно возобновить
stopped - действующая, но остановленная вручную, можно возобновить
'''


class Client(Base):
    __tablename__ = 'clients'
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    activated_date: Mapped[date] = mapped_column(Date)
    subscribe_duration: Mapped[int] = mapped_column(Integer, default=None, nullable=True)
    subscribe_status: Mapped[str] = mapped_column(String)
    peer_id: Mapped[str] = mapped_column(Integer)
    device: Mapped[str] = mapped_column(String)
    peer_name: Mapped[str] = mapped_column(String)


def check_clients_number(phone_number: str) -> List[Client]:
    with Session(engine) as session:
        stmt = select(Client).where(Client.phone_number == phone_number)
        result = session.execute(stmt).fetchall()
        return [i[0] for i in result]


if __name__ == '__main__':
    a = check_clients_number('+79608509010')
    print(a)
