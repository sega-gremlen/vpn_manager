import logging
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

logger = logging.getLogger(__name__)  # Логгер для текущего модуля/файла


jobstores = {'default': SQLAlchemyJobStore(url=settings.get_database_url(sync=True))}
scheduler = AsyncIOScheduler(jobstores=jobstores)


async def start_scheduler():
    scheduler.start()
    await add_traffic_monitor_job()


async def traffic_reset(telegram_id):
    await PanelApi.reset_clients_traffic(telegram_id)


async def traffic_monitor_job():
    """ Мониторинг статистики пользователей.
    Записываем в periods.values.
    Сделано, что бы потом можно было отселить статистику использования.
    Потом возможно сделаю историю трафика.
    """

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


async def add_traffic_reset_job(telegram_id: int,
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
        logger.info(f'Дата завершения работы меньше текущей даты для {telegram_id}')
        return

    job_id = f'trf_reset_{telegram_id}'

    # Старт и стоп потому что этот поток запускается отдельно (??)
    scheduler.start()

    # Удаляем старую работу если вдруг такая имеется
    job = scheduler.get_job(job_id)
    if job:
        scheduler.remove_job(job.id)

    trigger = IntervalTrigger(
        days=days_interval,
        start_date=start_date,
        end_date=end_date
    )



    new_job = scheduler.add_job(
        traffic_reset,
        trigger=trigger,
        args=[telegram_id],
        id=job_id,
    )
    scheduler.shutdown()

    logger.info(f'Работа по перезапуску трафика {new_job} для пользователя {telegram_id} добавлена')


async def add_traffic_monitor_job():
    """ Добавление работы по мониторингу статистики пользователей """

    if not scheduler.get_job('traffic_monitor'):
        scheduler.add_job(
            traffic_monitor_job,
            'interval',
            seconds=60,
            id='traffic_monitor'
        )
        logger.info('Работа по мониторингу статистики пользователей добавлена')


async def current_jobs():
    """ Вывести список текущих работ """

    curr_jobs = []
    for job in scheduler.get_jobs():
        start_date = job.trigger.start_date
        end_date = job.trigger.end_date
        next_run_time = job.next_run_time
        instances = job.max_instances
        curr_jobs.append(f'{job.id} \n'
                         f'start date: {start_date},\n'
                         f'end date: {end_date}\n'
                         f'next_execute: {next_run_time}\n'
                         f'instances: {instances}')
    return '\n-----'.join(curr_jobs)


async def update_traffic_reset_job_date(telegram_id, new_end_date):
    """ Обновление даты окончания работы """

    scheduler.start()
    job_id = f'trf_reset_{telegram_id}'
    job_trigger = scheduler.get_job(job_id).trigger
    new_trigger = IntervalTrigger(
        days=job_trigger.interval.days,
        start_date=job_trigger.start_date,
        end_date=new_end_date
    )
    scheduler.modify_job(job_id, trigger=new_trigger)
    scheduler.shutdown()
    logger.info(f'Работа по обновлению трафика для пользователя {telegram_id} выполнена'
                f'Новая дата окончания {new_end_date}')


async def pause_traffic_monitor(self):
    """ Пауза Aps """

    self.scheduler.pause()
    logger.info('Остановили мониторинг')
