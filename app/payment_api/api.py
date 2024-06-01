import copy
import uuid
from datetime import datetime as dt
from datetime import date, timedelta
from typing import Annotated
import pprint
import hashlib
import pytz
import os

from app.db.dao.base import BaseDAO
from app.db.payment_requests.models import PaymentRequests
from app.db.subscriptions.dao import Subscriptions, SubscriptionsDAO
from app.db.subscribe_types.dao import SubscriptionTypes, SubscriptionTypesDAO
from app.db.payments.dao import PaymentsDAO, Payments
from app.db.payment_requests.dao import PaymentRequestsDAO
from app.db.users.dao import UsersDAO
from app.db.users.models import Users
from app.main_interface import MainInterface

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
import uvicorn
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.bot.core.main import bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from app.bot.core.utils.statesform import BuySubSteps
# from aiogram import Bot

app = FastAPI()
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'static')
templates_path = os.path.join(static_path, 'templates')
templates = Jinja2Templates(directory=templates_path)
bot_message = None

notification_secret = 'RyrJP/v4ornHDNAd8hpKmJS1'  # todo спрятать в env

# operation_id = 904035776918098009
# notification_type = p2p-incoming
# datetime = 2014-04-28T16:31:28Z
# sha1_hash = 8693ddf402fe5dcc4c4744d466cabada2628148c
# sender = 41003188981230
# codepro = false
# currency = 643
# amount = 0.99
# withdraw_amount = 1.00
# label = YM.label.12345

# https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=5&label=4b670290-b73a-4396-a66c-0960ea3f982a

# @app.post("/payment_notification")
# async def process_payment(request: Request):
#     body = await request.body()
#     body_str = body.decode()
#     print(body_str)  # 'a=b&c=d'
#     return {"message": "Данные успешно обработаны"}

data = {
    'notification_type': 'card-incoming',
    'bill_id': '',
    'amount': '4.85',
    'codepro': 'false',
    'withdraw_amount': '5.00',
    'unaccepted': 'false',
    'label': '4b670290-b73a-4396-a66c-0960ea3f982a',
    'datetime': '2024-02-29T18:57:26Z',
    'sender': '',
    'sha1_hash': '4d8c9abbe818ec9f158f0e215f703c480a46a695',
    'operation_label': '2d72e745-0011-5000-a000-1c531b25ba94',
    'operation_id': '762548246564417096',
    'currency': '643'
}


@app.post('/payment_notification')
async def get_payment(
        notification_type: Annotated[str, Form()],
        operation_id: Annotated[str, Form()],
        datetime: Annotated[str, Form()],
        sha1_hash: Annotated[str, Form()],
        codepro: Annotated[str, Form()],  # параметр всегда имеет значение false
        currency: Annotated[str, Form()],
        amount: Annotated[str, Form()],
        operation_label: Annotated[str, Form()],
        sender: Annotated[str, Form()] = '',
        withdraw_amount: Annotated[str, Form()] = '',
        label: Annotated[str, Form()] = '',
        unaccepted: Annotated[str, Form()] = '',
        bill_id: Annotated[str, Form()] = '',  # не беру в бд
):
    payment = {
        'bill_id': bill_id,
        'operation_label': operation_label,
        'notification_type': notification_type,
        'operation_id': operation_id,
        'amount': amount,
        'currency': currency,
        'datetime': datetime,
        'sender': sender,
        'codepro': codepro,
        'sha1_hash': sha1_hash,
        'label': label,
        'unaccepted': unaccepted,
        'withdraw_amount': withdraw_amount,
    }

    pprint.pprint(payment)

    # if not await check_hash(payment):
    #     print('Хэш не совпадает')
    #     return {}

    payment_request: PaymentRequests = await PaymentRequestsDAO.find_one_or_none(label=payment['label'])

    if not payment_request:
        print('Данного запроса на оплату не существует')
        return {}

    if not await check_payment_amount(payment_request, payment['withdraw_amount']):
        print('Оплаченная сумма не соответствует выставляемой')
        return {}

    # На случай если оплаитл пользователь с уже активной подпиской
    last_active_sub: Subscriptions = await MainInterface().check_existing_sub(payment_request.telegram_id)
    if last_active_sub:
        start = last_active_sub.stop + timedelta(days=1)
    else:
        start = date.today()

    stop = start + timedelta(days=30 * payment_request.periods)
    created_at = dt.now()

    subscription = await SubscriptionsDAO.create(
        user_id=payment_request.user_id,
        subscription_type=payment_request.subscription_type,
        created_at=created_at,
        start=start,
        stop=stop,
    )

    await PaymentsDAO.create(
        subscription_id=subscription.id,
        user_id=payment_request.user_id,
        created_at=created_at,

        # Параметры api yoomoney
        notification_type=payment['notification_type'],
        operation_id=payment['operation_id'],
        operation_label=payment['operation_label'],
        amount=float(payment['amount']),
        withdraw_amount=float(payment['withdraw_amount']),
        currency=int(payment['currency']),
        api_datetime=dt.strptime(payment['datetime'][:-1], "%Y-%m-%dT%H:%M:%S"),
        sender=payment['sender'],
        label=payment['label'],
        sha1_hash=payment['sha1_hash'],
        unaccepted=True if payment['unaccepted'] == 'true' else False,
    )

    await PaymentRequestsDAO.patch_some(payment_request, completed=True)

    await bot_message.edit_text


# async def send_tg_succes_message(message: Message, state: FSMContext, telegram_id):
async def send_tg_succes_message(telegram_id, state: FSMContext):
    print(state.get_data())
    # bot.message.edit_message_text()
    # history = await bot.get_chat_history(telegram_id)
    # last_message: Message = history[-1]
    # await last_message.edit_text(text='Все dsdfsdfsd')


async def check_hash(data_to_check):
    # Строка полученной оплаты
    # notification_type&operation_id&amount&currency&datetime&sender&codepro&notification_secret&label
    # notification_type&operation_id&amount&currency&datetime&sender&codepro&notification_secret&label
    data_to_check = data_to_check.copy()

    sha_input = (
        f'{data_to_check["notification_type"]}&'
        f'{data_to_check["operation_id"]}&'
        f'{data_to_check["amount"]}&'
        f'{data_to_check["currency"]}&'
        # f'{data_to_check["datetime"].strftime("%Y-%m-%dT%H:%M:%SZ")}&'
        f'{data_to_check["datetime"]}&'
        f'{data_to_check["sender"]}&'
        f'{data_to_check["codepro"]}&'
        f'{notification_secret}&'
        f'{data_to_check["label"]}'
    )

    print(sha_input)

    generated_hash = hashlib.sha1()
    generated_hash.update(sha_input.encode('utf-8'))
    generated_hash = generated_hash.hexdigest()

    if generated_hash == data_to_check['sha1_hash']:
        return True
    return False


async def check_payment_amount(payment_request, withdraw_amount):
    subscription_type = await SubscriptionTypesDAO.find_one_or_none(name=payment_request.subscription_type)
    subscription_sum = subscription_type.price * payment_request.periods

    print('withdraw_amount', withdraw_amount)
    print('subscription_sum', subscription_sum)

    if float(subscription_sum) == float(withdraw_amount):
        return True
    return False


@app.get("/redirect/{label}")
async def create_proxy_url(request: Request, label: str):
    # http://localhost:8000/redirect/188e9987-c048-4df5-956c-429b16c6a3df

    # Поиск label в бд
    payment_request: PaymentRequests = await PaymentRequestsDAO.find_one_or_none(label=label)

    # Если нет label в бд
    if payment_request is None:
        return templates.TemplateResponse(request=request, name='label_not_found.html')

    # Если уже оплачено
    if payment_request.completed:
        return templates.TemplateResponse(request=request, name='payment_completed.html')

    # Если время истекло
    if payment_request.stop_at < dt.now():
        return templates.TemplateResponse(request=request, name='outdated_request.html')

    # Если существует более новая ссылка
    last_payment_request: PaymentRequests = await PaymentRequestsDAO().find_last_payment_request(
        payment_request.user_id)
    if payment_request.id != last_payment_request.id:
        return templates.TemplateResponse(request=request, name='newer_url_exists.html')

    # Если нет ошибок
    global bot_message
    bot_message = await bot.send_message(payment_request.telegram_id, 'Ждём подтверждения оплаты...')
    return RedirectResponse(url=payment_request.redirect_url)


if __name__ == "__main__":
    uvicorn.run("app.payment_api.api:app", host="localhost", port=8000, reload=True)
