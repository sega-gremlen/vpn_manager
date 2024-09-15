import zoneinfo
from datetime import datetime, timedelta

from app.aps import aps



async def test_add_traffic_reset_job():
    """ Проверяем правильность создания работы по сбросу трафика """

    telegram_test_id = 777
    dt_now = datetime.now(tz=zoneinfo.ZoneInfo(key='Europe/Moscow'))
    start_date = dt_now - timedelta(days=150)
    end_date = dt_now + timedelta(days=150)
    next_run_time = start_date + timedelta(days=((dt_now - start_date).days // 30 + 1) * 30)

    await aps.add_traffic_reset_job(telegram_test_id, start_date, end_date, 30)
    job = aps.scheduler.get_job(str(telegram_test_id))

    assert job is not None
    assert job.id == str(telegram_test_id)
    assert job.trigger.start_date == start_date
    assert job.trigger.end_date == end_date
    assert job.next_run_time == next_run_time


async def test_update_traffic_reset_job_date():
    """ Проверяем правильность обновления даты окончания """

    telegram_test_id = 777
    dt_now = datetime.now(tz=zoneinfo.ZoneInfo(key='Europe/Moscow'))
    start_date = dt_now - timedelta(days=150)
    end_date = dt_now + timedelta(days=150)

    await aps.add_traffic_reset_job(telegram_test_id, start_date, end_date, 30)
    job = aps.scheduler.get_job(str(telegram_test_id))
    new_end_date = job.trigger.end_date + timedelta(days=30 * 6)
    await aps.update_traffic_reset_job_date(str(telegram_test_id), new_end_date)
    updated_job = aps.scheduler.get_job(str(telegram_test_id))

    assert updated_job is not None
    assert updated_job.trigger.end_date == new_end_date
