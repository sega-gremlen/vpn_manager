from app.tests.data.utils import *

periods = [
    {
        "subscription_id": 1,
        "start": sub_1_start,
        "stop": sub_1_start + timedelta(days=30)
    },
    {
        "subscription_id": 1,
        "start": sub_1_start + timedelta(days=30),
        "stop": sub_1_start + timedelta(days=60)
    },
    {
        "subscription_id": 1,
        "start": sub_1_start + timedelta(days=60),
        "stop": sub_1_start + timedelta(days=90)
    },
    {
        "subscription_id": 1,
        "start": sub_1_start + timedelta(days=90),
        "stop": sub_1_start + timedelta(days=120),
    },
    {
        "subscription_id": 1,
        "start": sub_1_start + timedelta(days=120),
        "stop": sub_1_start + timedelta(days=150),
    },
    {
        "subscription_id": 1,
        "start": sub_1_start + timedelta(days=150),
        "stop": sub_1_start + timedelta(days=180),
    },
    {
        "subscription_id": 2,
        "start": sub_2_start,
        "stop": sub_2_start + timedelta(days=30),
    },
    {
        "subscription_id": 2,
        "start": sub_2_start + timedelta(days=30),
        "stop": sub_2_start + timedelta(days=60),
    },
    {
        "subscription_id": 2,
        "start": sub_2_start + timedelta(days=60),
        "stop": sub_2_start + timedelta(days=90),
    },
    {
        "subscription_id": 2,
        "start": sub_2_start + timedelta(days=90),
        "stop": sub_2_start + timedelta(days=120),
    },
    {
        "subscription_id": 2,
        "start": sub_2_start + timedelta(days=120),
        "stop": sub_2_start + timedelta(days=150),
    },
    {
        "subscription_id": 2,
        "start": sub_2_start + timedelta(days=150),
        "stop": sub_2_start + timedelta(days=180),
    },
    {
        "subscription_id": 3,
        "start": sub_3_start,
        "stop": sub_3_start + timedelta(days=14),
    },
    {
        "subscription_id": 4,
        "start": sub_4_start,
        "stop": sub_4_start + timedelta(days=30),
    }
]
