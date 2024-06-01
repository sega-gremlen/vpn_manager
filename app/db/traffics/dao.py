import asyncio
from datetime import datetime, date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, join, Row, RowMapping

from app.db.traffics.models import Traffics
from app.db.subscriptions.dao import Subscriptions
from app.db.periods.dao import Periods
from app.db.dao.base import BaseDAO
from app.db.creator import async_sessionmaker
from typing import Sequence, Any


class TrafficsDAO(BaseDAO):
    model = Traffics

    async def write_users_stat(self, users_stat: dict) -> dict:
        """
        Функция для записи прочитанного с помощью Xray трафика всех пользователей

        :param users_stat:
        :return: объемы скачанного и загруженного трафика всех пользователей
        с действующей подпиской за текущий период в байтах
        """
        users_general_stat = {}

        async with async_sessionmaker() as session:
            for user_id, traffic in users_stat.items():
                print('Пользователь ', user_id)

                all_traffic = await self._read_user_stat(session, user_id)

                if not all_traffic[0]:
                    print(f'Отсутствуют данные о траффике в связи с отсутствием подписки')
                    continue

                last_traffic = all_traffic[0][-1]

                data_to_insert = {
                    "period_id": last_traffic.period_id,
                    "created_at": datetime.now(),
                    "downlink": traffic['downlink'],
                    "uplink": traffic['uplink']
                }

                # Записываем трафик
                if last_traffic:
                    print(f'Есть существующий трафик у пользвоателя {user_id}')
                    if last_traffic.downlink < traffic['downlink'] or last_traffic.uplink < traffic['uplink']:
                        print(f'Есть изменение в трафике')
                        last_traffic.uplink = traffic['uplink']
                        last_traffic.downlink = traffic['downlink']
                    elif last_traffic.downlink == traffic['downlink'] and last_traffic.uplink == traffic['uplink']:
                        print('Нет изменений в трафике')
                    else:
                        print('Произошел рестарт, создаём новую запись')
                        await session.execute(insert(self.model).values(data_to_insert))
                else:
                    await session.execute(insert(self.model).values(data_to_insert))
                    print(f'Не было записей о трафике, создали первую')

                users_general_stat[user_id] = all_traffic[1]

            await session.commit()
        return users_general_stat

    async def read_user_stat(self, user_id: int) -> dict:
        """
        Функция для чтения трафика за текущий период

        :param user_id:
        :return: скаченный и загруженный трафик в байтах
        """
        async with async_sessionmaker() as session:
            user_stat = await self._read_user_stat(session, user_id)
            return user_stat[1]

    async def _read_user_stat(self, session: AsyncSession, user_id: int)\
            -> tuple[Sequence[Row | RowMapping | Any], dict]:
        """
        Внутренняя функция для чтения трафика пользователя за текущий период

        :param session:
        :param user_id:
        :return: кортеж из двух элементов: все записи трафика, скаченный и загруженный трафик в байтах
        """
        user_stat = {
            'downlink': 0,
            'uplink': 0,
        }
        date_today = date.today()

        # Выбираем текущий период и последнюю запсь о трафике в нём
        all_traffic = select(Traffics, Periods, Subscriptions).where(
            (Subscriptions.user_id == user_id) &
            (Periods.start <= date_today) &
            (Periods.stop >= date_today)
        ).select_from(join(Periods, Subscriptions, Periods.subscription_id == Subscriptions.id).
                      join(Traffics, self.model.period_id == Periods.id)).order_by(Traffics.created_at)
        all_traffic = await session.execute(all_traffic)
        all_traffic = all_traffic.scalars().all()

        # Формируем текущий общий трафик за текущий период
        for traffic_obj in all_traffic:
            user_stat['downlink'] += traffic_obj.downlink
            user_stat['uplink'] += traffic_obj.uplink

        return all_traffic, user_stat


if __name__ == '__main__':
    a = TrafficsDAO()
    print(asyncio.run(a.read_user_stat(1)))
