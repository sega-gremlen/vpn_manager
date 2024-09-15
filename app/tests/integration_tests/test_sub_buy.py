import copy
import zoneinfo

from aiogram import Dispatcher, Bot
from aiogram.methods import SendMessage, EditMessageText
from httpx import AsyncClient

from app.aps import aps
from app.bot.main import activate_subscription
from app.db.payment_requests.dao import PaymentRequestsDAO
from app.db.payment_requests.models import PaymentRequests
from app.db.payments.dao import PaymentsDAO
from app.db.payments.models import Payments
from app.db.periods.dao import PeriodsDAO
from app.db.periods.models import Periods
from app.db.subscription_types.dao import SubscriptionTypesDAO
from app.db.subscription_types.models import SubscriptionTypes
from app.db.subscriptions.dao import SubscriptionsDAO
from app.db.subscriptions.models import Subscriptions
from app.db.users.dao import UsersDAO
from app.db.users.models import Users
from app.main_interface import main_interface
from app.panel_3x_ui_api import PanelApi
from app.tests.conftest import dispatcher, memory_storage
from app.tests.data.utils import *
from config import settings
from app.tests.data.mock_users import users


async def check_panel_conf(tg_user_id, sub_obj):
    panel_user = await PanelApi.get_client_from_inbound(tg_user_id)
    assert panel_user is not None
    assert panel_user['success'] == True
    assert panel_user['obj']['inboundId'] == settings.INBOUND_ID
    assert panel_user['obj']['enable'] == True
    assert panel_user['obj']['email'] == str(tg_user_id)
    assert panel_user['obj']['up'] == 0
    assert panel_user['obj']['down'] == 0
    assert panel_user['obj']['expiryTime'] == int(sub_obj.stop.timestamp()) * 1000
    assert panel_user['obj']['total'] == settings.TRAFFIC_LIMIT * 1024 ** 3
    assert panel_user['obj']['reset'] == 0


async def tg_bot_menu_navigating(dispatcher: Dispatcher,
                                 bot: Bot,
                                 tg_user_id: int,
                                 tg_chat_id: int,
                                 test_case: str = None):
    """ Для навигации по боту

    1 - купить пробную подписку
    2 - купить подписку на 6 месяцев
    """

    # Главное меню
    res: SendMessage = await dispatcher.feed_update(
        bot=bot,
        update=get_update(message=get_message('/start', tg_user_id, tg_chat_id),
                          )
    )
    assert isinstance(res, SendMessage)
    # todo прописать параметры для проверки

    # Выбираем купить подписку
    update = get_update(call=get_callback_querry('buy_sub', tg_user_id, tg_chat_id))
    res: SendMessage = await dispatcher.feed_update(
        bot=bot,
        update=update
    )
    assert isinstance(res, EditMessageText)
    # todo прописать параметры для проверки

    if test_case == 'trial':

        # Выбираем пробную подписку
        update = get_update(call=get_callback_querry('trial', tg_user_id, tg_chat_id))
        res: SendMessage = await dispatcher.feed_update(
            bot=bot,
            update=update
        )
        assert isinstance(res, EditMessageText)
        # todo прописать параметры для проверки

        # Активируем пробную подписку
        update = get_update(call=get_callback_querry('activate_trial', tg_user_id, tg_chat_id))
        res: SendMessage = await dispatcher.feed_update(
            bot=bot,
            update=update
        )
        assert isinstance(res, SendMessage)
        # todo прописать параметры для проверки

    else:
        # Выбираем платную подписку
        res: SendMessage = await dispatcher.feed_update(
            bot=bot,
            update=get_update(call=get_callback_querry('type_6', tg_user_id, tg_chat_id))
        )
        assert isinstance(res, EditMessageText)
        # todo прописать параметры для проверки

        # Переходим по ссылке на оплату
        res: SendMessage = await dispatcher.feed_update(
            bot=bot,
            update=get_update(call=get_callback_querry('pay_url', tg_user_id, tg_chat_id))
        )
        assert isinstance(res, SendMessage)
        # todo прописать параметры для проверки

    return res


# Офрмляем юзер 1
# Оформление первой подписки-пробной
async def test_first_trial_sub_buy(dispatcher: Dispatcher, bot: Bot):
    """
    Тестируемое событие:
    - Пользователь первой подпиской оформляет в боте пробную

    Вводные:
    - запись в бд с пользователем, trial-wasted=0

    Всё что происходит после нажатия на кнопку "да, оформить" в боте
    Проверить:
    - Смена trial-wasted - статуса
    - Создание записи подписки в бд: даты
    - Создание записи периодов в бд
    - Создание записи периодов в бд
    - Создание клиента на панели: его duration, limit
    - Создание урла и его соответствие правильному
    - Вывод сообщений в боте
    """

    tg_user_id = user_1_tg
    chat_id = random.randint(1, 10000000)

    res = await tg_bot_menu_navigating(dispatcher, bot, tg_user_id, chat_id, test_case='trial')

    # Проверяем смену trial-wasted - статуса
    user: Users = await UsersDAO.find_one_or_none(telegram_id=user_1_tg)
    assert user is not None
    assert user.xray_uuid == users[0]['xray_uuid']
    assert user.trial_wasted == True

    # Проверяем корректность создания url
    url_test = (f'vless://{user.xray_uuid}@'
                f'{settings.PANEL_HOST}:{settings.INBOUND_PORT}?'
                f'type=tcp&'
                f'security=reality&'
                f'pbk={settings.PUBKEY}&'
                f'fp=chrome&'
                f'sni=yahoo.com&'
                f'sid={settings.SID}&'
                f'spx=/&'
                f'flow=xtls-rprx-vision#'
                f'{settings.PROFILE_NAME}')
    assert url_test in res.text

    # Проверяем корректность создания записи подписки в бд
    sub: Subscriptions = await SubscriptionsDAO.find_one_or_none(user_id=user.id)
    end_sub = dt_now + timedelta(days=14)
    assert sub is not None
    assert sub.subscription_type_id == 4
    assert ((sub.start.year, sub.start.month, sub.start.day, sub.start.hour) == 
            (dt_now.year, dt_now.month, dt_now.day, dt_now.hour))
    assert ((sub.stop.year, sub.stop.month, sub.stop.day, sub.stop.hour) ==
            (end_sub.year, end_sub.month, end_sub.day, end_sub.hour))

    # Проверяем корректность создания записи периода в бд
    per: Periods = await PeriodsDAO.find_one_or_none(subscription_id=sub.id)
    assert per is not None
    assert sub.start == per.start
    assert sub.stop == per.stop
    assert per.current_value == 0

    # Проверяем корректность создания записи юзера на панели
    panel_user = await PanelApi.get_client_from_inbound(user_1_tg)
    assert panel_user is not None
    assert panel_user['success'] == True
    assert panel_user['obj']['inboundId'] == settings.INBOUND_ID
    assert panel_user['obj']['enable'] == True
    assert panel_user['obj']['email'] == str(tg_user_id)
    assert panel_user['obj']['up'] == 0
    assert panel_user['obj']['down'] == 0
    assert panel_user['obj']['expiryTime'] == int(sub.stop.timestamp()) * 1000
    assert panel_user['obj']['total'] == settings.TRAFFIC_LIMIT * 1024 ** 3
    assert panel_user['obj']['reset'] == 0


# Оформление первой обычной подписки
async def test_first_simple_sub_buy(dispatcher: Dispatcher, bot: Bot, ac: AsyncClient, memory_storage):
    """
    Тестируемое событие:
    - Пользователь первой подпиской оформляет в боте простую

    Вводные:
    - запись в бд с пользователем, trial-wasted=0

    Проверить:
    - Смена trial-wasted - статуса
    - Создание записи payment requests в бд
    - Создание записи payments в бд
    - Создание записи подписки в бд: даты
    - Создание записи периодов в бд
    - Создание клиента на панели: его duration, limit
    - Создание работы aps и её параметров
    - Создание урла
    - Вывод сообщений в боте
    """

    tg_user_id = user_1_tg
    chat_id = random.randint(1, 10000000)
    user: Users = await UsersDAO.find_one_or_none(telegram_id=tg_user_id)
    assert user is not None

    res = await tg_bot_menu_navigating(dispatcher, bot, tg_user_id, chat_id)

    # Проверяем корректность создания записи payment_request в бд
    pay_req: PaymentRequests = await PaymentRequestsDAO.find_last_by_filter(
        'created_at',
        telegram_id=tg_user_id)
    assert pay_req is not None
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=pay_req.subscription_type_id)
    assert sub_type is not None
    assert pay_req.periods == 6
    assert pay_req.subscription_type_id == sub_type.id
    assert pay_req.completed == False
    assert ('https://yoomoney.ru/quickpay/confirm/?'
            f'receiver={settings.RECIEVER}&'
            f'quickpay-form=button&'
            f'paymentType=AC&'
            f'sum={sub_type.price}&'
            f'label=') in pay_req.redirect_url
    assert pay_req.stop_at - pay_req.created_at == timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME)

    # Переходим по ссылке
    response = await ac.get(f'/redirect/{pay_req.label}')
    print(response.text)
    assert response.status_code == 307

    #Считаем хэш
    operation_id = str(random.randint(100000000000000000, 999999999999999999))
    sha_input = (
        'card-incoming&'
        f'{operation_id}&'
        f'{sub_type.price - (sub_type.price * 0.03):.2f}&'
        '643&'
        f'{dt_now.strftime('%Y-%m-%dT%H:%M:%SZ')}&'
        '&'
        'false&'
        f'{settings.NOTI_SECRET}&'
        f'{pay_req.label}'
    )
    sha1_hash = main_interface.generate_hash(sha_input)

    # Отсылаем деньги
    data = {
        'notification_type': 'card-incoming',
        'bill_id': '',
        'amount': f'{sub_type.price - (sub_type.price * 0.03):.2f}',
        'codepro': 'false',
        'withdraw_amount': f'{sub_type.price:.2f}',
        'unaccepted': 'false',
        'label': pay_req.label,
        'datetime': dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'sender': '',
        'sha1_hash': sha1_hash,
        'operation_label': '2d72e745-0011-5000-a000-1c531b25ba94&',
        'operation_id': operation_id,
        'currency': '643'
    }
    response = await ac.post(
        '/payment_notification',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=data,
    )
    assert response.status_code == 200

    # Запускаем активацию подписки
    state = get_state(chat_id, tg_user_id, bot, memory_storage)
    response = await activate_subscription(response.json(), bot, state)

    # Проверяем корректность создания url
    url_test = (f'vless://{user.xray_uuid}@'
                f'{settings.PANEL_HOST}:{settings.INBOUND_PORT}?'
                f'type=tcp&'
                f'security=reality&'
                f'pbk={settings.PUBKEY}&'
                f'fp=chrome&'
                f'sni=yahoo.com&'
                f'sid={settings.SID}&'
                f'spx=/&'
                f'flow=xtls-rprx-vision#'
                f'{settings.PROFILE_NAME}')
    assert url_test in response

    # Проверяем смену trial-wasted - статуса
    user: Users = await UsersDAO.find_one_or_none(telegram_id=tg_user_id)
    assert user is not None
    assert user.trial_wasted == True

    # Проверяем создание подписки
    sub: Subscriptions = await SubscriptionsDAO.find_one_or_none(user_id=user.id)
    assert sub is not None
    assert sub.subscription_type_id == sub_type.id
    end_sub = dt_now + timedelta(days=180)
    assert ((sub.start.year, sub.start.month, sub.start.day, sub.start.hour) ==
            (dt_now.year, dt_now.month, dt_now.day, dt_now.hour))
    assert ((sub.stop.year, sub.stop.month, sub.stop.day, sub.stop.hour) ==
            (end_sub.year, end_sub.month, end_sub.day, end_sub.hour))

    # Проверяем корректность создания записи периодов в бд
    per: Periods = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == sub.id)
    assert per is not None
    assert len(per) == pay_req.periods
    assert per[0].start == sub.start
    assert per[-1].stop == sub.stop

    # Проверяем создание записи об оплате
    pay: Payments = await PaymentsDAO.find_one_or_none(subscription_id=sub.id)
    assert pay.user_id == user.id
    assert pay.notification_type == data['notification_type']
    assert pay.operation_id == data['operation_id']
    assert pay.operation_label == data['operation_label']
    assert pay.amount == float(data['amount'])
    assert pay.withdraw_amount == float(data['withdraw_amount'])
    assert pay.currency == int(data['currency'])
    assert pay.api_datetime == datetime.strptime(dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'), '%Y-%m-%dT%H:%M:%SZ')
    assert pay.sender == data['sender']
    assert pay.label == data['label']
    assert pay.sha1_hash == data['sha1_hash']
    assert pay.unaccepted == False

    # Проверяем корректность создания записи юзера на панели
    # panel_user = await PanelApi.get_client_from_inbound(user.telegram_id)
    # assert panel_user is not None
    # assert panel_user['success'] == True
    # assert panel_user['obj']['inboundId'] == settings.INBOUND_ID
    # assert panel_user['obj']['enable'] == True
    # assert panel_user['obj']['email'] == str(tg_user_id)
    # assert panel_user['obj']['up'] == 0
    # assert panel_user['obj']['down'] == 0
    # assert panel_user['obj']['expiryTime'] == int(sub.stop.timestamp()) * 1000
    # assert panel_user['obj']['total'] == settings.TRAFFIC_LIMIT * 1024 ** 3
    # assert panel_user['obj']['reset'] == 0
    await check_panel_conf(tg_user_id, sub)


    # Проверяем корректность создания работы
    job = aps.scheduler.get_job(str(tg_user_id))
    assert job is not None
    assert job.trigger.interval.days == 30
    assert job.trigger.start_date == sub.start.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    assert job.trigger.end_date == sub.stop.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    assert job.next_run_time == per[1].start.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))


# Оформление обычной подписки во время активной текущей пробной
async def test_sub_buy_with_active_trial_sub(dispatcher: Dispatcher, bot: Bot, ac: AsyncClient, memory_storage):
    """
    Тестируемое событие:
    - Пользователь во время активной пробной подписки хочет оформить полноценную

    Вводные:
    - запись в бд с пользователем trial-wasted=1
    - запись в бд с существующей подпиской пробной, оформленной не более 14 дней назад
    - запись в бд периода подписки с рандомным трафиком
    - наличие клиента на панели с duration не более 14 дней

    Проверить:
    - Создание записи payment requests в бд и её параметры
    - Создание записи payments в бд и её параметры
    - Создание записи основной подписки в бд
    - Создание периодов основной подписки в бд и их параметры
    - Увеличение duration клиента на панели
    - Создание работы aps и её параметров
    - Вывод сообщений в боте
    """

    tg_user_id = user_4_tg
    chat_id = random.randint(1, 10000000)

    #Проверяем вводные
    user: Users = await UsersDAO.find_one_or_none(telegram_id=tg_user_id)
    assert user is not None
    assert user.trial_wasted == True
    sub: Subscriptions = await SubscriptionsDAO.find_one_or_none(user_id=user.id)
    assert sub is not None
    assert sub.stop - sub.start == timedelta(days=14)
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=sub.subscription_type_id)
    assert sub_type is not None
    assert sub_type.name == 'trial'
    per: Periods = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == sub.id)
    assert len(per) == 1
    assert per[0].start == sub.start
    assert per[0].stop == sub.stop
    await check_panel_conf(tg_user_id, sub)

    await tg_bot_menu_navigating(dispatcher, bot, tg_user_id, chat_id)

    # Проверяем корректность создания записи payment_request в бд
    pay_req: PaymentRequests = await PaymentRequestsDAO.find_last_by_filter(
        'created_at',
        telegram_id=tg_user_id)
    assert pay_req is not None
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=pay_req.subscription_type_id)
    assert sub_type is not None
    assert pay_req.periods == 6
    assert pay_req.subscription_type_id == sub_type.id
    assert pay_req.completed == False
    assert ('https://yoomoney.ru/quickpay/confirm/?'
            f'receiver={settings.RECIEVER}&'
            f'quickpay-form=button&'
            f'paymentType=AC&'
            f'sum={sub_type.price}&'
            f'label=') in pay_req.redirect_url
    assert pay_req.stop_at - pay_req.created_at == timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME)

    # Переходим по ссылке
    response = await ac.get(f'/redirect/{pay_req.label}')
    print(response.text)
    assert response.status_code == 307

    # Считаем хэш
    operation_id = str(random.randint(100000000000000000, 999999999999999999))
    sha_input = (
        'card-incoming&'
        f'{operation_id}&'
        f'{sub_type.price - (sub_type.price * 0.03):.2f}&'
        '643&'
        f'{dt_now.strftime('%Y-%m-%dT%H:%M:%SZ')}&'
        '&'
        'false&'
        f'{settings.NOTI_SECRET}&'
        f'{pay_req.label}'
    )
    sha1_hash = main_interface.generate_hash(sha_input)

    # Отсылаем деньги
    data = {
        'notification_type': 'card-incoming',
        'bill_id': '',
        'amount': f'{sub_type.price - (sub_type.price * 0.03):.2f}',
        'codepro': 'false',
        'withdraw_amount': f'{sub_type.price:.2f}',
        'unaccepted': 'false',
        'label': pay_req.label,
        'datetime': dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'sender': '',
        'sha1_hash': sha1_hash,
        'operation_label': '2d72e745-0011-5000-a000-1c531b25ba94&',
        'operation_id': operation_id,
        'currency': '643'
    }
    response = await ac.post(
        '/payment_notification',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=data,
    )
    assert response.status_code == 200

    # Запускаем активацию подписки
    state = get_state(chat_id, tg_user_id, bot, memory_storage)
    response = await activate_subscription(response.json(), bot, state)

    # Проверяем выход response
    assert response is None

    # Проверяем корректность завершения текущей пробной подписки
    sub: Subscriptions = await SubscriptionsDAO.find_one_or_none(id=sub.id)
    assert sub is not None
    assert sub.stop < datetime.now()
    per: Periods = await PeriodsDAO.find_one_or_none(id=per[0].id)
    assert sub is not None
    assert per.stop == sub.stop

    # Проверяем создание новой подписки
    sub: Subscriptions = await SubscriptionsDAO.find_last_subscription_by_user_id(user_id=user.id)
    assert sub.subscription_type_id == sub_type.id
    end_sub = dt_now + timedelta(days=180)
    assert ((sub.start.year, sub.start.month, sub.start.day, sub.start.hour) ==
            (dt_now.year, dt_now.month, dt_now.day, dt_now.hour))
    assert ((sub.stop.year, sub.stop.month, sub.stop.day, sub.stop.hour) ==
            (end_sub.year, end_sub.month, end_sub.day, end_sub.hour))

    # Проверяем корректность создания записи периодов в бд
    per: Periods = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == sub.id)
    assert per is not None
    assert len(per) == pay_req.periods
    assert per[0].start == sub.start
    assert per[-1].stop == sub.stop

    # Проверяем создание записи об оплате
    pay: Payments = await PaymentsDAO.find_one_or_none(subscription_id=sub.id)
    assert pay.user_id == user.id
    assert pay.notification_type == data['notification_type']
    assert pay.operation_id == data['operation_id']
    assert pay.operation_label == data['operation_label']
    assert pay.amount == float(data['amount'])
    assert pay.withdraw_amount == float(data['withdraw_amount'])
    assert pay.currency == int(data['currency'])
    assert pay.api_datetime == datetime.strptime(dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'), '%Y-%m-%dT%H:%M:%SZ')
    assert pay.sender == data['sender']
    assert pay.label == data['label']
    assert pay.sha1_hash == data['sha1_hash']
    assert pay.unaccepted == False

    # Проверяем корректность создания записи юзера на панели
    await check_panel_conf(tg_user_id, sub)
    # panel_user = await PanelApi.get_client_from_inbound(user.telegram_id)
    # assert panel_user is not None
    # assert panel_user['success'] == True
    # assert panel_user['obj']['inboundId'] == settings.INBOUND_ID
    # assert panel_user['obj']['enable'] == True
    # assert panel_user['obj']['email'] == str(tg_user_id)
    # assert panel_user['obj']['up'] == 0
    # assert panel_user['obj']['down'] == 0
    # assert panel_user['obj']['expiryTime'] == int(sub.stop.timestamp()) * 1000
    # assert panel_user['obj']['total'] == settings.TRAFFIC_LIMIT * 1024 ** 3
    # assert panel_user['obj']['reset'] == 0

    # Проверяем корректность создания работы
    job = aps.scheduler.get_job(str(tg_user_id))
    assert job is not None
    assert job.trigger.interval.days == 30
    assert job.trigger.start_date == sub.start.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    assert job.trigger.end_date == sub.stop.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    assert job.next_run_time == per[1].start.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))


# Оформление обычной подписки во время активной текущей обычной
async def test_sub_buy_with_active_simple_sub(dispatcher: Dispatcher,
                                              bot: Bot,
                                              ac: AsyncClient,
                                              memory_storage):
    """
    Тестируемое событие:
    - Пользователь во время активной простой подписки хочет её продлить

    Вводные:
    - запись в бд с пользователем trial-wasted=1
    - запись в бд с активной простой подпиской
    - запись в бд простой подписки
    - запись в бд периода подписки с рандомным трафиком
    - наличие активного клиента на панели трафик не превышен
    - работа aps

    Проверить:
    - Создание записи payment requests в бд и её параметры
    - Создание записи payments в бд и её параметры
    - Изменение в записи даты окончания основной подписки в бд
    - Создание периодов основной подписки в бд и их параметры
    - Увеличение duration клиента на панели
    - Изменение даты окончания работы
    - Вывод сообщений в боте
    """
    ...

    tg_user_id = user_3_tg
    chat_id = random.randint(1, 10000000)

    #Проверяем вводные
    user: Users = await UsersDAO.find_one_or_none(telegram_id=tg_user_id)
    assert user is not None
    assert user.trial_wasted == True
    sub: Subscriptions = await SubscriptionsDAO.find_one_or_none(user_id=user.id)
    assert sub is not None
    assert sub.stop - sub.start == timedelta(days=180)
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=sub.subscription_type_id)
    assert sub_type is not None
    assert sub_type.name == 'type_6'
    per: list[Periods] = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == sub.id)
    assert len(per) == 6
    assert per[0].start == sub.start
    assert per[-1].stop == sub.stop
    await check_panel_conf(tg_user_id, sub)
    pay_req: PaymentRequests = await PaymentRequestsDAO.find_one_or_none(telegram_id=tg_user_id)
    assert pay_req is not None
    assert pay_req.completed == True
    assert pay_req.periods == 6

    await tg_bot_menu_navigating(dispatcher, bot, tg_user_id, chat_id)

    # Проверяем корректность создания записи payment_request в бд
    pay_req: PaymentRequests = await PaymentRequestsDAO.find_last_by_filter(
        'created_at',
        telegram_id=tg_user_id)
    assert pay_req is not None
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=pay_req.subscription_type_id)
    assert sub_type is not None
    assert pay_req.periods == 6
    assert pay_req.subscription_type_id == sub_type.id
    assert pay_req.completed == False
    assert ('https://yoomoney.ru/quickpay/confirm/?'
            f'receiver={settings.RECIEVER}&'
            f'quickpay-form=button&'
            f'paymentType=AC&'
            f'sum={sub_type.price}&'
            f'label=') in pay_req.redirect_url
    assert pay_req.stop_at - pay_req.created_at == timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME)

    # Переходим по ссылке
    response = await ac.get(f'/redirect/{pay_req.label}')
    print(response.text)
    assert response.status_code == 307

    # Считаем хэш
    operation_id = str(random.randint(100000000000000000, 999999999999999999))
    sha_input = (
        'card-incoming&'
        f'{operation_id}&'
        f'{sub_type.price - (sub_type.price * 0.03):.2f}&'
        '643&'
        f'{dt_now.strftime('%Y-%m-%dT%H:%M:%SZ')}&'
        '&'
        'false&'
        f'{settings.NOTI_SECRET}&'
        f'{pay_req.label}'
    )
    sha1_hash = main_interface.generate_hash(sha_input)

    # Отсылаем деньги
    data = {
        'notification_type': 'card-incoming',
        'bill_id': '',
        'amount': f'{sub_type.price - (sub_type.price * 0.03):.2f}',
        'codepro': 'false',
        'withdraw_amount': f'{sub_type.price:.2f}',
        'unaccepted': 'false',
        'label': pay_req.label,
        'datetime': dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'sender': '',
        'sha1_hash': sha1_hash,
        'operation_label': '2d72e745-0011-5000-a000-1c531b25ba94&',
        'operation_id': operation_id,
        'currency': '643'
    }
    response = await ac.post(
        '/payment_notification',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=data,
    )
    assert response.status_code == 200

    # Запускаем активацию подписки
    state = get_state(chat_id, tg_user_id, bot, memory_storage)
    response = await activate_subscription(response.json(), bot, state)

    # Проверяем выход response
    assert response is None

    # Проверяем корректность продления текущей подписки

    old_sub: Subscriptions = copy.copy(sub)
    sub: Subscriptions = await SubscriptionsDAO.find_one_or_none(id=sub.id)

    assert sub is not None
    assert old_sub.id == sub.id
    assert old_sub.stop < sub.stop
    assert sub.stop - old_sub.stop == timedelta(days=180)
    assert sub.start == old_sub.start

    # per: Periods = await PeriodsDAO.find_one_or_none(id=per[0].id)
    # assert sub is not None
    # assert per.stop == sub.stop

    # Проверяем корректность создания записи периодов в бд
    per: list[Periods] = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == sub.id)
    assert per is not None
    assert len(per) == pay_req.periods + 6
    assert per[0].start == sub.start == old_sub.start
    assert per[-1].stop == sub.stop

    # Проверяем создание записи об оплате
    pay: Payments = await PaymentsDAO.find_last_by_filter('id', subscription_id=sub.id)
    assert pay.user_id == user.id
    assert pay.notification_type == data['notification_type']
    assert pay.operation_id == data['operation_id']
    assert pay.operation_label == data['operation_label']
    assert pay.amount == float(data['amount'])
    assert pay.withdraw_amount == float(data['withdraw_amount'])
    assert pay.currency == int(data['currency'])
    assert pay.api_datetime == datetime.strptime(dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'), '%Y-%m-%dT%H:%M:%SZ')
    assert pay.sender == data['sender']
    assert pay.label == data['label']
    assert pay.sha1_hash == data['sha1_hash']
    assert pay.unaccepted == False

    # Проверяем корректность продления юзера на панели
    await check_panel_conf(tg_user_id, sub)

    # Проверяем корректность обновления даты окончания работы
    job = aps.scheduler.get_job(str(tg_user_id))
    assert job is not None
    assert job.trigger.interval.days == 30
    assert job.trigger.start_date == sub.start.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    assert job.trigger.end_date == sub.stop.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    current_per: Periods = await PeriodsDAO.find_current_period_sub(tg_user_id)
    assert job.next_run_time == current_per.stop.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))


# Оформление обычной подписки спустя время после окончания предыдущей любой
async def test_sub_buy_without_active_sub(dispatcher: Dispatcher,
                                          bot: Bot,
                                          ac: AsyncClient,
                                          memory_storage):
    """
    Тестируемое событие:
    - Пользователь после окончания простой подписки хочет её продлить

    Вводные:
    - запись в бд с пользователем trial-wasted=1
    - запись в бд с активной простой подпиской
    - запись в бд простой подписки
    - запись в бд периода подписки с рандомным трафиком
    - наличие активного клиента на панели трафик не превышен
    - старая работа aps

    Проверить:
    - Создание записи payment requests в бд и её параметры
    - Создание записи payments в бд и её параметры
    - Изменение в записи даты окончания основной подписки в бд
    - Создание периодов основной подписки в бд и их параметры
    - Увеличение duration клиента на панели
    - Создание новой работы
    - Вывод сообщений в боте
    """
    tg_user_id = user_5_tg
    chat_id = random.randint(1, 10000000)

    #Проверяем вводные
    user: Users = await UsersDAO.find_one_or_none(telegram_id=tg_user_id)
    assert user is not None
    assert user.trial_wasted == True
    sub: Subscriptions = await SubscriptionsDAO.find_one_or_none(user_id=user.id)
    assert sub is not None
    assert sub.stop < dt_now
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=sub.subscription_type_id)
    assert sub_type is not None
    assert sub_type.name != 'trial'
    per: list[Periods] = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == sub.id)
    assert len(per) == 1
    assert per[0].start == sub.start
    assert per[-1].stop == sub.stop
    await check_panel_conf(tg_user_id, sub)
    pay_req: PaymentRequests = await PaymentRequestsDAO.find_one_or_none(telegram_id=tg_user_id)
    assert pay_req is not None
    assert pay_req.completed == True
    assert pay_req.periods == 1

    await tg_bot_menu_navigating(dispatcher, bot, tg_user_id, chat_id)

    # Проверяем корректность создания записи payment_request в бд
    pay_req: PaymentRequests = await PaymentRequestsDAO.find_last_by_filter(
        'created_at',
        telegram_id=tg_user_id)
    assert pay_req is not None
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=pay_req.subscription_type_id)
    assert sub_type is not None
    assert pay_req.periods == 6
    assert pay_req.subscription_type_id == sub_type.id
    assert pay_req.completed == False
    assert ('https://yoomoney.ru/quickpay/confirm/?'
            f'receiver={settings.RECIEVER}&'
            f'quickpay-form=button&'
            f'paymentType=AC&'
            f'sum={sub_type.price}&'
            f'label=') in pay_req.redirect_url
    assert pay_req.stop_at - pay_req.created_at == timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME)

    # Переходим по ссылке
    response = await ac.get(f'/redirect/{pay_req.label}')
    print(response.text)
    assert response.status_code == 307

    # Считаем хэш
    operation_id = str(random.randint(100000000000000000, 999999999999999999))
    sha_input = (
        'card-incoming&'
        f'{operation_id}&'
        f'{sub_type.price - (sub_type.price * 0.03):.2f}&'
        '643&'
        f'{dt_now.strftime('%Y-%m-%dT%H:%M:%SZ')}&'
        '&'
        'false&'
        f'{settings.NOTI_SECRET}&'
        f'{pay_req.label}'
    )
    sha1_hash = main_interface.generate_hash(sha_input)

    # Отсылаем деньги
    data = {
        'notification_type': 'card-incoming',
        'bill_id': '',
        'amount': f'{sub_type.price - (sub_type.price * 0.03):.2f}',
        'codepro': 'false',
        'withdraw_amount': f'{sub_type.price:.2f}',
        'unaccepted': 'false',
        'label': pay_req.label,
        'datetime': dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'sender': '',
        'sha1_hash': sha1_hash,
        'operation_label': '2d72e745-0011-5000-a000-1c531b25ba94&',
        'operation_id': operation_id,
        'currency': '643'
    }
    response = await ac.post(
        '/payment_notification',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=data,
    )
    assert response.status_code == 200

    # Запускаем активацию подписки
    state = get_state(chat_id, tg_user_id, bot, memory_storage)
    response = await activate_subscription(response.json(), bot, state)

    # Проверяем выход response
    assert response is None

    # Проверяем корректность оформления новой подписки
    old_sub = copy.copy(sub)
    sub: Subscriptions = await SubscriptionsDAO.find_last_subscription_by_user_id(user_id=user.id)
    assert sub is not None
    assert sub != old_sub

    # Проверяем корректность создания записи периодов в бд
    per: list[Periods] = await PeriodsDAO.find_all_by_filter(Periods.subscription_id == sub.id)
    assert per is not None
    assert len(per) == 6
    assert per[0].start == sub.start
    assert per[-1].stop == sub.stop

    # Проверяем создание записи об оплате
    pay: Payments = await PaymentsDAO.find_last_by_filter('id', subscription_id=sub.id)
    assert pay.user_id == user.id
    assert pay.notification_type == data['notification_type']
    assert pay.operation_id == data['operation_id']
    assert pay.operation_label == data['operation_label']
    assert pay.amount == float(data['amount'])
    assert pay.withdraw_amount == float(data['withdraw_amount'])
    assert pay.currency == int(data['currency'])
    assert pay.api_datetime == datetime.strptime(dt_now.strftime('%Y-%m-%dT%H:%M:%SZ'), '%Y-%m-%dT%H:%M:%SZ')
    assert pay.sender == data['sender']
    assert pay.label == data['label']
    assert pay.sha1_hash == data['sha1_hash']
    assert pay.unaccepted == False

    # Проверяем корректность продления юзера на панели
    await check_panel_conf(tg_user_id, sub)

    # Проверяем корректность создания новой работы
    job = aps.scheduler.get_job(str(tg_user_id))
    assert job is not None
    assert job.trigger.interval.days == 30
    assert job.trigger.start_date == sub.start.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    assert job.trigger.end_date == sub.stop.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
    current_per: Periods = await PeriodsDAO.find_current_period_sub(tg_user_id)
    assert job.next_run_time == current_per.stop.replace(tzinfo=zoneinfo.ZoneInfo(key='Europe/Samara'))
