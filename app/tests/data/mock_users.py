from datetime import datetime

from app.tests.data.utils import *

users = [
    # 1 Юзер без подписки
    {
        "telegram_id": user_1_tg,
        "created_at": datetime.fromisoformat("2024-06-06 15:20:00.000"),
        "xray_uuid": "23f60103-5a00-44f2-95fb-36cd5bd7c137",
        "trial_wasted": False
    },
    # 2 Юзер с активной подпиской
    {
        "telegram_id": user_2_tg,
        "created_at": sub_1_start - timedelta(days=1),
        "xray_uuid": "c771e2d0-670f-4393-a3cf-9e8da3fa4d18",
        "trial_wasted": True
    },
    # 3 Юзер с активной подпиской
    {
        "telegram_id": user_3_tg,
        "created_at": sub_2_start - timedelta(days=1),
        "xray_uuid": "aa21d1e1-108f-47e4-b435-b1fbe8015d4e",
        "trial_wasted": True
    },
    # 4 Юзер с активной пробной подпиской
    {
        "telegram_id": user_4_tg,
        "created_at": sub_3_start - timedelta(days=1),
        "xray_uuid": "cd35537b-d9b8-41a4-b157-42dceb805397",
        "trial_wasted": True
    },

    # 5 Юзер с завершенной подпиской
    {
        "telegram_id": user_5_tg,
        "created_at": sub_4_start - timedelta(days=1),
        "xray_uuid": "662707da-9fbc-46e6-913c-1074b3da21b3",
        "trial_wasted": True
    }
]

if __name__ == '__main__':
    print(users)
