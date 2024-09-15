import asyncio
import zoneinfo
from datetime import datetime

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.periods.dao import PeriodsDAO
from app.db.periods.models import Periods
from app.db.users.dao import UsersDAO
from app.panel_3x_ui_api import PanelApi
from config import settings


async def traffic_reset(telegram_id):
    await PanelApi.reset_clients_traffic(telegram_id)


async def traffic_monitor_job():
    """ Мониторинг статистики пользователей.
    Записываем в periods.values.
    Сделано, что бы потом можно было отселить статистику использования.
    Потом возможно сделаю историю трафика.
    """

    # dt_now = datetime.now()
    users_subscriptions_periods = await UsersDAO.get_users_with_active_sub()

    for data_row in users_subscriptions_periods:
        user_traffic = await PanelApi.get_client_traffics_with_email(data_row.telegram_id)
        user_period: Periods = await PeriodsDAO.find_one_or_none(id=data_row.id_2)
        await PeriodsDAO.patch(user_period, current_value=user_traffic)


async def subscribe_end_notification():
    """ Уведомление пользователя о скором окончании подписки """
    ...

async def traffic_end_notification():
    """ Уведомление пользователя о скором окончании лимита трафика """
    ...


class Aps:
    def __init__(self):
        jobstores = {'default': SQLAlchemyJobStore(url=settings.get_database_url(sync=True))}
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)


    async def add_traffic_reset_job(self, telegram_id: int,
                                    start_date: datetime,
                                    end_date: datetime,
                                    days_interval: int):
        """ Добавление работы по перезапуску трафика для пользователя """

        # Проверка на корректность даты окончания введенной работы
        # Костыль с датами нужен для тестов, при создании триггера проставляется автоматически временная зона
        # Поэтому временную зону нужно вставлять вручную, в этом случае сравнивать с датой без tz нельзя
        try:
            tz_obj = zoneinfo.ZoneInfo(key=str(end_date.tzinfo))
            dt_now = datetime.now(tz=tz_obj)
        except zoneinfo.ZoneInfoNotFoundError:
            dt_now = datetime.now()

        if end_date < dt_now:
            print(f'Дата завершения работы меньше текущей даты для {telegram_id}')
            return

        job_id = str(telegram_id)

        # Удаляем старую работу если вдруг такая имеется
        job = aps.scheduler.get_job(job_id)
        if job:
            aps.scheduler.remove_job(job.id)

        trigger = IntervalTrigger(
            days=days_interval,
            start_date=start_date,
            end_date=end_date
        )

        aps.scheduler.add_job(
            traffic_reset,
            trigger=trigger,
            args=[telegram_id],
            id=job_id,
        )

        print(f'Работа по перезапуску трафика для пользователя {telegram_id} добавлена')


    async def add_traffic_monitor_job(self):
        """ Добавление работы по мониторингу статистики пользователей """

        if not self.scheduler.get_job('traffic_monitor'):
            self.scheduler.add_job(
                traffic_monitor_job,
                'interval',
                seconds=60,
                id='traffic_monitor'
            )
            print('Работа по мониторингу статистики пользователей добавлена')


    async def my_jobs(self):
        """ Вывести список текущих работ """

        for job in self.scheduler.get_jobs():
            start_date = job.trigger.start_date
            end_date = job.trigger.end_date
            next_run_time = job.next_run_time
            instances = job.max_instances
            print(f'{job.name} for {job.id}\n'
                  f'start date: {start_date},\n'
                  f'end date: {end_date}\n'
                  f'next_execute: {next_run_time}\n'
                  f'instances: {instances}\n---------')


    async def update_traffic_reset_job_date(self, telegram_id, new_end_date):
        """ Вывод информации о конкретной работе """

        job_trigger = self.scheduler.get_job(str(telegram_id)).trigger
        print('интервал', job_trigger.interval.days)
        new_trigger = IntervalTrigger(
            days=job_trigger.interval.days,
            start_date=job_trigger.start_date,
            end_date=new_end_date
        )
        self.scheduler.modify_job(str(telegram_id), trigger=new_trigger)

        print(f'Работа по обновлению трафика для пользователя {telegram_id} обновлена')



    # async def geeeet(self):
    #     self.scheduler.get_job()



    async def pause_traffic_monitor(self):
        """ Пауза Aps """

        self.scheduler.pause()
        print('Остановили мониторинг')


aps = Aps()


if __name__ == '__main__':
    async def main():
        aps.scheduler.start()
        await asyncio.sleep(500)

    asyncio.run(main())
