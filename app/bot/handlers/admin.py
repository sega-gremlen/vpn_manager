import re
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.db.payments.dao import PaymentsDAO
from app.db.payments.models import Payments
from app.db.periods.dao import PeriodsDAO
from app.db.periods.models import Periods
from app.db.subscriptions.dao import SubscriptionsDAO
from app.db.subscriptions.models import Subscriptions
from app.db.users.dao import UsersDAO
from app.db.users.models import Users
from app.panel_3x_ui_api import PanelApi
from app.bot.utils.statesform import Admin
from app.aps import current_jobs



async def refund_sub_enter(message: Message, state: FSMContext) -> None:
    """
    Расчет средств для возврата если подписка еще не закончилась
    Возврат происходит по ссылке которую присылает пользователь из бота.
    Берем последнюю активную подписку.
    Исходим из расчета неиспользованных в подписке дней
    """

    await message.answer('Пришлите conf-url пользователя')
    await state.set_state(Admin.REFUND_SUB)


async def refund_sub_get_url(message: Message, state: FSMContext):
    await state.set_state(Admin.GET_CONF_URL)

    # Ищем юзера по конфиг-ссылке
    conf_url_uuid = re.search(r'vless://(.*?)@', message.text).group(1)
    user: Users = await UsersDAO.find_one_or_none(xray_uuid=conf_url_uuid)

    # Ищем подписку на удаление
    sub_to_refund: Subscriptions = await SubscriptionsDAO.find_last_sub_by_user_tg_id(user.telegram_id)
    if not sub_to_refund:
        return ...

    # Ищем оплату пользователя
    user_payment: Payments = await PaymentsDAO.find_last_by_filter('id',
                                                                   subscription_id=sub_to_refund.id)

    print(user_payment)
    # Удаляем периоды, подписку и удаляем из панели
    await PeriodsDAO.delete_all_by_filter(Periods.subscription_id == sub_to_refund.id)
    await SubscriptionsDAO.delete_all_by_filter(Subscriptions.id == sub_to_refund.id)
    await PanelApi.delete_client_from_inbound(conf_url_uuid)

    if user_payment:
        dt_now = datetime.now()
        date_range_to_refound = (sub_to_refund.stop - dt_now).days
        share_to_refound = date_range_to_refound / (sub_to_refund.stop - sub_to_refund.start).days
        money_to_refound = int(share_to_refound * user_payment.withdraw_amount)
        await message.answer(f'Денег к возврату: {money_to_refound} за неиспользованных {date_range_to_refound} дней')
    else:
        await message.answer('Денег возвращать не нужно, подписка бесплатная')

    await state.clear()


async def add_user_get_tg_id(message: Message, state: FSMContext):
    await message.answer('Пришлите имя пользователя')
    await state.set_state(Admin.ADD_USER)


async def add_vip_user(message: Message, state: FSMContext):
    ...


async def get_curr_jobs(message: Message, state: FSMContext):
    curr_jobs: str = await current_jobs()
    await message.answer(text=curr_jobs)


