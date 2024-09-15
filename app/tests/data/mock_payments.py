from app.tests.data.utils import *

payments = [
    # Юзер с активной подпиской
    {
        "subscription_id": 1,
        "user_id": 2,
        "created_at": sub_1_start,
        "notification_type": "card-incoming",
        "operation_id": "200000000000000000",
        "operation_label": "2dc920c9-9c52-4e49-9abd-81e6afa29219",
        "amount": 388.0,
        "withdraw_amount": 400.0,
        "currency": 643,
        "api_datetime": sub_1_start,
        "sender": "",
        "label": "103d718d-1eda-4251-bfac-b1fe0a704b01",
        "sha1_hash": "9c894d0aba67f959dfc6124abba3781369201b04",
        "unaccepted": False
    },

    # Юзер с активной подпиской
    {
        "subscription_id": 2,
        "user_id": 3,
        "created_at": sub_2_start,
        "notification_type": "card-incoming",
        "operation_id": "300000000000000000",
        "operation_label": "2b30a540-458e-4a95-9b74-9fede57325f7",
        "amount": 388.0,
        "withdraw_amount": 400.0,
        "currency": 643,
        "api_datetime": sub_2_start,
        "sender": "",
        "label": "1c684534-5c91-4443-bd8f-f5cfd821a441",
        "sha1_hash": "3f60c82494593ff905fe19c413b05c0e47f15b61",
        "unaccepted": False
    },

    # Юзер с активной подпиской
    # {
    #     "subscription_id": 3,
    #     "user_id": 4,
    #     "created_at": sub_3_start,
    #     "notification_type": "card-incoming",
    #     "operation_id": "400000000000000000",
    #     "operation_label": "45e405c4-3acc-4834-9218-20ec40033a4d",
    #     "amount": 388.0,
    #     "withdraw_amount": 400.0,
    #     "currency": 643,
    #     "api_datetime": sub_3_start,
    #     "sender": "",
    #     "label": "4a89062e-35db-4ad3-8bb5-fa0f8e7c9c6f",
    #     "sha1_hash": "ae5f5a5142fccf9af0edffd488ec1e584934967f",
    #     "unaccepted": False
    # },

    # Юзер с завершенной подпиской
    {
        "subscription_id": 4,
        "user_id": 5,
        "created_at": sub_4_start,
        "notification_type": "card-incoming",
        "operation_id": "500000000000000000",
        "operation_label": "043657a4-7ba5-4ab6-a19e-228e735f5483",
        "amount": 77.6,
        "withdraw_amount": 80.0,
        "currency": 643,
        "api_datetime": sub_4_start,
        "sender": "",
        "label": "69f35136-fdfb-44c6-b6af-2a20d5d281f7",
        "sha1_hash": "c9c9865ff035d43b121c4e07864875af6029ddd9",
        "unaccepted": False
    }
]
