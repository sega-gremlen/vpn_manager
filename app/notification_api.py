import logging
from datetime import datetime as dt
from typing import Annotated
import os

from fastapi import FastAPI, Form, HTTPException, status, Response
from starlette.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
# import uvicorn

from app.db.payment_requests.models import PaymentRequests
from app.db.payment_requests.dao import PaymentRequestsDAO
from app.main_interface import main_interface
from config import settings
from app.bot.main import activate_subscription, send_error_msg
from app.bot.main import bot


app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Шаблоны для ответов на редирект ссылке
api_templates = Jinja2Templates(directory=settings.API_TEMPLATES_PATH)

WrongHashSumm = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Хэш не совпадает',
        )


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
    """ Получение уведомления об оплате """

    logger.info(f'Получили оплату, payment_request: {label}')

    payment_data = {
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

    if not main_interface.check_hash(payment_data):
        raise WrongHashSumm

    if os.getenv('MODE') in ('PROD', 'DEV'):
        # Не знаю как это прокрутить в тесте
        await activate_subscription(payment_data, bot)
        return Response(status_code=200)
    else:
        return payment_data


@app.get("/redirect/{label}")
async def create_proxy_url(request: Request, label: str):
    """ Создание редирект ссылки типа:
    http://localhost:8000/redirect/188e9987-c048-4df5-956c-429b16c6a3df
    """

    # Поиск label в бд
    payment_request: PaymentRequests = await PaymentRequestsDAO.find_one_or_none(label=label)

    # Если нет label в бд
    if payment_request is None:
        logger.info('Нет label в бд')
        return api_templates.TemplateResponse(
            request=request,
            name='label_not_found.html',
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Если уже оплачено
    if payment_request.completed:
        logger.info('Уже оплачено')
        await send_error_msg(bot, payment_request.telegram_id) if settings.MODE in ('DEV', 'PROD') else ...
        return api_templates.TemplateResponse(
            request=request,
            name='payment_completed.html',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Если время истекло
    if payment_request.stop_at < dt.now():
        logger.info('Время истекло')
        await send_error_msg(bot, payment_request.telegram_id) if settings.MODE in ('DEV', 'PROD') else ...
        return api_templates.TemplateResponse(
            request=request,
            name='outdated_request.html',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Если существует более новая ссылка
    last_payment_request: PaymentRequests = await PaymentRequestsDAO().find_last_payment_request(
        payment_request.user_id)
    if payment_request.id != last_payment_request.id:
        logger.info('Существует более новая ссылка')
        await send_error_msg(bot, payment_request.telegram_id) if settings.MODE in ('DEV', 'PROD') else ...
        return api_templates.TemplateResponse(
            request=request,
            name='newer_url_exists.html',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return RedirectResponse(url=payment_request.redirect_url)
