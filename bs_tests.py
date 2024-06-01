import asyncio
from datetime import datetime
from app.db.users.dao import UsersDAO
from app.db.subscriptions.dao import SubscriptionsDAO
from app.db.subscribe_types.dao import SubscribeTypesDAO
from app.db.payments.dao import PaymentsDAO

from datetime import timedelta

import uuid


async def create_subscription():
    telegram_id = 11222343
    user = UsersDAO.find_one_or_none(telegram_id=telegram_id)
    if user is None:
        user = insert_user(tg_id='')
        sub = await insert_subscrption()
        await insert_payment(sub)


async def insert_user(tg_id):
    await UsersDAO.create(
        telegram_id=tg_id,
        created_at=datetime.now(),
        xray_uuid=uuid.uuid4()
    )


async def insert_payment(subscription_id):
    user = await UsersDAO.find_one_or_none(telegram_id=1231231)
    method = 'sber perevod'
    created_at = datetime.now()
    amount = 300

    await PaymentsDAO.create(
        method=method,
        created_at=created_at,
        amount=amount,
        subscription_id=subscription_id,
        user_id=user.id

    )


async def insert_subscrption():
    user = await UsersDAO.find_one_or_none(telegram_id=1231231)
    created_at = datetime.now()
    end_at = created_at + timedelta(days=30)
    user_id = user.id
    subscribe_type = await SubscribeTypesDAO.find_one_or_none(name='simple')

    sub = await SubscriptionsDAO.create(
        created_at=created_at,
        end_at=end_at,
        user_id=user_id,
        subscribe_type=subscribe_type.name
    )
    print(sub)
    return sub


if __name__ == '__main__':
    asyncio.run(create_subscription())
