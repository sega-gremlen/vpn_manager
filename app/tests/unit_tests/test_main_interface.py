import hashlib
import uuid
from datetime import datetime
import re

import requests
from asyncpg.pgproto.pgproto import timedelta

from app.db.payment_requests.models import PaymentRequests
from app.db.subscription_types.dao import SubscriptionTypesDAO
from app.db.subscription_types.models import SubscriptionTypes
from app.db.users.dao import UsersDAO, Users
from app.main_interface import main_interface
from config import settings

from app.bot.utils.jinja_templates import xray_url


async def test_create_user():
    test_tg_id = 7000000000
    new_user = await main_interface.create_user(test_tg_id)

    assert new_user.telegram_id == test_tg_id

    new_user = await main_interface.create_user(1000000000)

    assert new_user is None

async def test_check_existing_sub():
    test_tg_id_1 = 1000000000
    test_tg_id_2 = 2000000000

    sub = await main_interface.get_active_subscription(test_tg_id_1)
    assert sub is None

    sub = await main_interface.get_active_subscription(test_tg_id_2)
    assert sub is not None
    assert sub.id == 1

async def test_create_payment_request():
    test_tg_id = 1000000000
    sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(id=2)
    new_payment_request: PaymentRequests = await main_interface.create_payment_request(test_tg_id, sub_type)

    assert new_payment_request is not None
    assert new_payment_request.id == 7
    assert new_payment_request.telegram_id == test_tg_id
    assert new_payment_request.stop_at <= datetime.now() + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME + 10)
    assert new_payment_request.periods == int(sub_type.duration / 30)
    assert new_payment_request.subscription_type_id == sub_type.id
    assert new_payment_request.completed == False

    # Прооверяем ссылку
    redirect_url = new_payment_request.redirect_url.split('&')
    assert str(settings.RECIEVER) in redirect_url[0]
    assert 'quickpay-form=button' in redirect_url[1]
    assert 'paymentType=AC' in redirect_url[2]
    assert sub_type.price == int(redirect_url[3].split('=')[1])
    redirect_url_uuid = redirect_url[4].split('=')[1]
    assert str(uuid.UUID(redirect_url_uuid, version=4)) == redirect_url_uuid
    response = requests.get(new_payment_request.redirect_url)
    assert response.status_code == 200

async def test_render_xray_url():
    # Пример рабочей ссылки
    # vless://6efdc299-cfc1-47e2-a5d1-52f5d1f4b1b5@95.182.122.43:443?security=
    # reality&encryption=none&alpn=h2&pbk=6z8Zc9mwmes3LX6iijrwJynZzjTmszjp5IIWOqvaSA4&
    # headerType=none&fp=chrome&type=tcp&flow=xtls-rprx-vision&
    # sni=www.yahoo.com&sid=14a2a8e1387d1f4f#rus

    user_to_url_test: Users = await UsersDAO.find_one_or_none(telegram_id=2000000000)

    test_xray_url = await main_interface.render_xray_url(user_to_url_test.xray_uuid)
    test_xray_url = xray_url.render(test_xray_url)

    assert test_xray_url is not None

    pattern = re.compile(r"vless://(?P<uuid>[0-9a-fA-F\-]+)@"
                         r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3}):\d+\?"
                         r"(?P<params>(?:[a-zA-Z0-9]+=[^&]+&?)+)#.*")

    match = pattern.match(test_xray_url)

    if match:
        assert user_to_url_test.xray_uuid == match.group('uuid')
        assert settings.PANEL_HOST == match.group('ip')

        params = match.group('params')
        # Используем регулярное выражение для разделения параметров
        param_pattern = re.compile(r"(?P<key>[a-zA-Z0-9]+)=(?P<value>[^&]+)")
        param_matches = param_pattern.findall(params)
        param_matches = {key: value for key, value in param_matches}

        assert param_matches['security'] =='reality'
        assert param_matches['pbk'] == settings.PUBKEY
        assert param_matches['fp'] == 'chrome'
        assert param_matches['type'] == 'tcp'
        assert param_matches['flow'] == 'xtls-rprx-vision'
        assert param_matches['sni'] == settings.MASK_HOST
        assert param_matches['sid'] == settings.SID

    profile_name = test_xray_url.split('#')[1][:-6]
    assert profile_name == settings.PROFILE_NAME

    # урл скопированный с панели
    assert test_xray_url[5:-6] == ('vless://c771e2d0-670f-4393-a3cf-9e8da3fa4d18@localhost:47141?type='
                              'tcp&security=reality&pbk=6z8Zc9mwmes3LX6iijrwJynZzjTmszjp5IIWOqvaSA4&'
                              'fp=chrome&sni=yahoo.com&sid=14a2a8e1387d1f4f&spx=/&'
                              'flow=xtls-rprx-vision#TEST')


def test_generate_hash():
    assert main_interface.generate_hash('hello') == hashlib.sha1('hello'.encode('utf-8')).hexdigest()


def test_check_hash():
    test_data_input = {
        'notification_type': 'card-incoming',
        'bill_id': '',
        'amount': f'{77.60:.2f}',
        'codepro': 'false',
        'withdraw_amount': f'{80.00:.2f}',
        'unaccepted': 'false',
        'label': '3e2be2ac-8771-4923-bbad-125940a6d9df',
        'datetime': '2024-02-29T18:57:26Z',
        'sender': '',
        'sha1_hash': '849e3756087ee4de541e7bfdd0a0ddc118672b5e',
        'operation_label': '2d72e745-0011-5000-a000-1c531b25ba94&',
        'operation_id': '762548246564417096',
        'currency': '643'
    }

    assert main_interface.check_hash(test_data_input) == True

async def test_create_redirect_url():
    ...

async def test_find_last_active_subscription():
    ...

def test_make_payment_url():
    ...

def test_watch_user_stat():
    ...

async def test_read_user_db_stat():
    ...

async def test_create_test_statistic_data():
    ...









