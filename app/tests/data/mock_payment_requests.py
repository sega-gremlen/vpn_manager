from app.tests.data.utils import *
from config import settings

payment_requests = [
    # Для теста, нормальная
    {
        "user_id": 1,
        "telegram_id": 1000000000,
        "label": "3e2be2ac-8771-4923-bbad-125940a6d9df",
        "created_at": dt_now,
        "stop_at": dt_now + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME),
        "periods": 1,
        "subscription_type_id": 1,
        "completed": False,
        "redirect_url": "https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=80&label=3e2be2ac-8771-4923-bbad-125940a6d9df"
    },

    # Для теста, время истекло
    {
        "user_id": 1,
        "telegram_id": 1000000000,
        "label": "3081c856-f0de-4047-b8d7-f10ad1b0faf0",
        "created_at": dt_now - timedelta(days=1),
        "stop_at": dt_now - timedelta(days=1) + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME),
        "periods": 6,
        "subscription_type_id": 2,
        "completed": False,
        "redirect_url": "https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=400&label=3081c856-f0de-4047-b8d7-f10ad1b0faf0"
    },

    # Для теста, существует более новая ссылка
    {
        "user_id": 1,
        "telegram_id": 1000000000,
        "label": "c9dd753a-1efb-452d-8d3f-a5ec3233ee00",
        "created_at": dt_now - timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME - 20),
        "stop_at": dt_now - timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME - 20) + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME),
        "periods": 6,
        "subscription_type_id": 2,
        "completed": False,
        "redirect_url": "https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=400&label=c9dd753a-1efb-452d-8d3f-a5ec3233ee00"
    },

    # Юзер с активной подпиской
    {
        "user_id": 2,
        "telegram_id": 2000000000,
        "label": "103d718d-1eda-4251-bfac-b1fe0a704b01",
        "created_at": sub_1_start - timedelta(seconds=200),
        "stop_at": sub_1_start - timedelta(seconds=200) + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME),
        "periods": 6,
        "subscription_type_id": 2,
        "completed": True,
        "redirect_url": "https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=400&label=103d718d-1eda-4251-bfac-b1fe0a704b01"
    },

    # Юзер с активной подпиской
    {
        "user_id": 3,
        "telegram_id": 3000000000,
        "label": "1c684534-5c91-4443-bd8f-f5cfd821a441",
        "created_at": sub_2_start - timedelta(seconds=200),
        "stop_at": sub_2_start - timedelta(seconds=200) + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME),
        "periods": 6,
        "subscription_type_id": 2,
        "completed": True,
        "redirect_url": "https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=400&label=1c684534-5c91-4443-bd8f-f5cfd821a441"
    },

    # Юзер с активной подпиской
    # {
    #     "user_id": 4,
    #     "telegram_id": 4000000000,
    #     "label": "4a89062e-35db-4ad3-8bb5-fa0f8e7c9c6f",
    #     "created_at": sub_3_start - timedelta(seconds=200),
    #     "stop_at": sub_3_start - timedelta(seconds=200) + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME),
    #     "periods": 6,
    #     "subscription_type_id": 2,
    #     "completed": True,
    #     "redirect_url": "https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=400&label=4a89062e-35db-4ad3-8bb5-fa0f8e7c9c6f"
    # },

    # Юзер с завершенной подпиской, тест на уже оплаченный запрос
    {
        "user_id": 5,
        "telegram_id": 5000000000,
        "label": "69f35136-fdfb-44c6-b6af-2a20d5d281f7",
        "created_at": sub_4_start - timedelta(seconds=200),
        "stop_at": sub_4_start - timedelta(seconds=200) + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME),
        "periods": 1,
        "subscription_type_id": 1,
        "completed": True,
        "redirect_url": "https://yoomoney.ru/quickpay/confirm/?receiver=4100118561425598&quickpay-form=button&paymentType=AC&sum=80&label=69f35136-fdfb-44c6-b6af-2a20d5d281f7"
    }
]
