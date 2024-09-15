import uuid

from app.db.dao.base import BaseDAO
from app.db.payments.dao import PaymentsDAO
from app.db.periods.dao import PeriodsDAO
from app.db.periods.models import Periods
from app.db.subscriptions.dao import SubscriptionsDAO
from app.db.subscriptions.models import Subscriptions
from app.db.users.dao import UsersDAO, Users
from app.tests.data.utils import *


async def test_user_create():
    user: Users = await UsersDAO.create(
        telegram_id=600000000,
        created_at=datetime.now(),
        xray_uuid=str(uuid.uuid4())
    )

    assert type(user) is Users
    assert user.telegram_id == 600000000
    assert user.id == 6


async def test_find_first_by_filter():
    sub: Subscriptions = await SubscriptionsDAO.find_first_by_filter(subscription_type_id=2)
    assert sub.id == 1


async def test_find_last_by_filter():
    sub = await SubscriptionsDAO.find_last_by_filter('id', subscription_type_id=2)
    assert sub.id == 2


async def test_find_all_by_filter():
    subs = await SubscriptionsDAO.find_all_by_filter(Subscriptions.subscription_type_id==2)
    assert len(subs) == 2


async def test_find_one_or_none_v1():
    payment = await PaymentsDAO.find_one_or_none(label='1c684534-5c91-4443-bd8f-f5cfd821a441')
    assert payment.id == 2


async def test_find_one_or_none_v2():
    payment = await PaymentsDAO.find_one_or_none(label='...')
    assert payment is None


async def test_patch():
    user: Users = await UsersDAO.find_one_or_none(telegram_id=user_1_tg)
    assert user.trial_wasted == False
    await BaseDAO.patch(user, trial_wasted=True)
    user: Users = await UsersDAO.find_one_or_none(telegram_id=user_1_tg)
    assert user.trial_wasted == True


async def test_join_request():
    user_sub = await UsersDAO.join_request(Subscriptions, Users.id==2)
    assert user_sub.telegram_id == 2000000000
    assert user_sub.id_1 == 1

async def test_find_current_period():
    current_period_user_2 = await PeriodsDAO.find_current_period_sub(user_2_tg)
    all_periods_user_2 = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == 1)
    assert current_period_user_2.id == all_periods_user_2[1].id
    assert current_period_user_2.start == all_periods_user_2[1].start
    assert current_period_user_2.stop == all_periods_user_2[1].stop

    current_period_user_3 = await PeriodsDAO.find_current_period_sub(user_3_tg)
    all_periods_user_3 = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == 2)
    assert current_period_user_3.id == all_periods_user_3[2].id
    assert current_period_user_3.start == all_periods_user_3[2].start
    assert current_period_user_3.stop == all_periods_user_3[2].stop

    current_period_user_4 = await PeriodsDAO.find_current_period_sub(user_4_tg)
    all_periods_user_4 = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == 3)
    assert current_period_user_4.id == all_periods_user_4[0].id
    assert current_period_user_4.start == all_periods_user_4[0].start
    assert current_period_user_4.stop == all_periods_user_4[0].stop

async def test_find_last_sub_by_user_tg_id():
    last_sub_user_1 = await SubscriptionsDAO.find_last_sub_by_user_tg_id(user_1_tg)
    assert last_sub_user_1 is None

    last_sub_user_2 = await SubscriptionsDAO.find_last_sub_by_user_tg_id(user_2_tg)
    assert last_sub_user_2 is not None
    assert last_sub_user_2.id == 1

    last_sub_user_3 = await SubscriptionsDAO.find_last_sub_by_user_tg_id(user_3_tg)
    assert last_sub_user_3 is not None
    assert last_sub_user_3.id == 2

    last_sub_user_4 = await SubscriptionsDAO.find_last_sub_by_user_tg_id(user_4_tg)
    assert last_sub_user_4 is not None
    assert last_sub_user_4.id == 3

    last_sub_user_5 = await SubscriptionsDAO.find_last_sub_by_user_tg_id(user_5_tg)
    assert last_sub_user_5 is not None
    assert last_sub_user_5.id == 4

async def test_find_last_sub_by_user_id():
    last_sub_user_1 = await SubscriptionsDAO.find_last_subscription_by_user_id(1)
    assert last_sub_user_1 is None

    last_sub_user_2 = await SubscriptionsDAO.find_last_subscription_by_user_id(2)
    assert last_sub_user_2 is not None
    assert last_sub_user_2.id == 1

    last_sub_user_3 = await SubscriptionsDAO.find_last_subscription_by_user_id(3)
    assert last_sub_user_3 is not None
    assert last_sub_user_3.id == 2

    last_sub_user_4 = await SubscriptionsDAO.find_last_subscription_by_user_id(4)
    assert last_sub_user_4 is not None
    assert last_sub_user_4.id == 3

    last_sub_user_5 = await SubscriptionsDAO.find_last_subscription_by_user_id(5)
    assert last_sub_user_5 is not None
    assert last_sub_user_5.id == 4




