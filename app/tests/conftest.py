import asyncio
from random import randint

from app.aps import aps

import pytest
from aiogram import Dispatcher
# from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import insert

from httpx import AsyncClient

from app.bot.main import register_user_handlers
from app.notification_api import app as fastapi_app


from app.db.creator import Base
from app.tests.data.mocked_bot import MockedBot
from config import settings
from app.db import creator


from app.db.periods.models import Periods
from app.db.users.models import Users
from app.db.payments.models import Payments
from app.db.subscriptions.models import Subscriptions
from app.db.subscription_types.models import SubscriptionTypes
from app.db.payment_requests.models import PaymentRequests

from app.tests.data.utils import *

from app.tests.data.mock_subscriptions import subscriptions
from app.tests.data.mock_users import users
from app.tests.data.mock_periods import periods
from app.tests.data.mock_payment_requests import payment_requests
from app.tests.data.mock_payments import payments
from app.tests.data.mock_subscription_types import subscription_types

from app.panel_3x_ui_api import PanelApi

@pytest.fixture(scope='function', autouse=True)
async def prepare_database():
    """ Подготовка тестовой базы данных """

    assert settings.MODE == 'TEST'

    await creator.create_database(settings.DB_NAME)

    async with creator.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with creator.async_sessionmaker() as session:
        add_users = insert(Users).values(users)
        add_subscription_types = insert(SubscriptionTypes).values(subscription_types)
        add_subscriptions = insert(Subscriptions).values(subscriptions)
        add_payment_requests = insert(PaymentRequests).values(payment_requests)
        add_payments = insert(Payments).values(payments)
        add_periods = insert(Periods).values(periods)

        await session.execute(add_users)
        await session.execute(add_subscription_types)
        await session.execute(add_subscriptions)
        await session.execute(add_payment_requests)
        await session.execute(add_payments)
        await session.execute(add_periods)

        await session.commit()


@pytest.fixture(scope='function', autouse=True)
async def prepare_3x_ui():
    """ Подготовка тестового входящего соединения 3x-ui """

    await PanelApi.del_inbound()
    await PanelApi.add_inbound()

    for user in users[1:]:
        user_id = users.index(user) + 1
        user_sub = list(filter(lambda x: x['user_id'] == user_id, subscriptions))
        await PanelApi.add_client_to_inbound(
            user['xray_uuid'],
            user['telegram_id'],
            user_sub[0]['stop']
        )

@pytest.fixture(scope='function', autouse=True)
async def start_aps():
    """ Подготовка тестового aps """

    try:
        aps.scheduler.start()
    except:
        pass


    await aps.add_traffic_reset_job(users[1]['telegram_id'],
                                    subscriptions[0]['start'],
                                    subscriptions[0]['stop'],
                                    30)

    await aps.add_traffic_reset_job(users[2]['telegram_id'],
                                    subscriptions[1]['start'],
                                    subscriptions[1]['stop'],
                                    30)

    await aps.add_traffic_reset_job(users[4]['telegram_id'],
                                    subscriptions[3]['start'],
                                    subscriptions[3]['stop'],
                                    30)

@pytest.fixture(scope='function')
async def ac():
    """ Тестовое http-соединение """

    async with AsyncClient(app=fastapi_app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='session')
async def memory_storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest.fixture(scope='session', name='bot')
def bot():
    return MockedBot()


@pytest.fixture(scope='session')
async def dispatcher():
    dp = Dispatcher()
    register_user_handlers(dp)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest.fixture(name="storage_key")
def create_storage_key(bot: MockedBot):
    return StorageKey(chat_id=randint(1, 1000000), user_id=randint(1, 1000000), bot_id=bot.id)


@pytest.fixture(scope='session')
def event_loop(request):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
