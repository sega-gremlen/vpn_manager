from app.tests.data.utils import *

subscriptions = [

    # Активная обычная подписка
    {
        "user_id": 2,
        "subscription_type_id": 2,
        "start": sub_1_start,
        "stop": sub_1_start + timedelta(days=180)
    },

    # Активная обычная подписка
    {
        "user_id": 3,
        "subscription_type_id": 2,
        "start": sub_2_start,
        "stop": sub_2_start + timedelta(days=180)
    },

    # Активная пробная подписка
    {
        "user_id": 4,
        "subscription_type_id": 4,
        "start": sub_3_start,
        "stop": sub_3_start + timedelta(days=14)
    },

    # Завершенная подписка
    {
        "user_id": 5,
        "subscription_type_id": 1,
        "start": sub_4_start,
        "stop": sub_4_start + timedelta(days=30)
    }
]
