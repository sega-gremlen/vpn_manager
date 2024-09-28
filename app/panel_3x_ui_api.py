import asyncio
import json
from datetime import datetime
import inspect

import aiohttp

from config import settings


class PanelApi:
    panel_address = f'http://{settings.PANEL_HOST}:{settings.PANEL_PORT}'
    login_address = f'{panel_address}/login'
    base_url = f'{panel_address}/panel/api/inbounds'
    params = {
        'username': settings.PANEL_USERNAME,
        'password': settings.PANEL_PASSWORD,
    }
    json_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


    @classmethod
    async def check_response(cls, response: aiohttp.ClientResponse) -> bool:
        """ Логи выполнения запросов """

        code_contexts = list((i.code_context[0] for i in inspect.stack()))
        api_request = list(filter(lambda x: 'PanelApi' in x, code_contexts))
        if api_request:
            print(f'Выполнение {api_request[0].strip()}:', end=' ')
        response_json = await response.json()

        if response_json['success']:
            print('запрос успешен')
            # print(response)
            # print(response_json)
            return True
        else:
            print('запрос не успешен')
            print(response)
            print(response_json)
            return False

    @classmethod
    async def generate_data_for_user(
            cls, user_uuid: str,
            user_telegram_id: int|str,
            expiry_time: datetime|int,
            traffic_limit: int,
            inbound_id: int
    ) -> dict:

        data = {
            "id": inbound_id,
            "settings": json.dumps({
                "clients": [
                    {
                        "id": user_uuid,
                        "flow": "xtls-rprx-vision",
                        "email": str(user_telegram_id),
                        "totalGB": traffic_limit,  # В гигабайтах
                        # Панель не воспринимает время без *1000
                        "expiryTime": int(expiry_time.timestamp()) * 1000 if expiry_time else 0,
                        "enable": True,
                    }
                ]

            })
        }

        return data


    @classmethod
    async def add_inbound(cls, inbound_id, profile_name, port, prvt_key, sid, pubkey) -> bool:
        """ Добавить входящее соединение """
        exist_inbound = await cls.get_inbound()
        if not exist_inbound:
            data = {
                "id": inbound_id,
                "userId": 0,
                "up": 0,
                "down": 0,
                "total": 0,
                "remark": profile_name,
                "enable": True,
                "expiryTime": 0,
                "listen": "",
                "port": port,
                "protocol": "vless",
                "settings": json.dumps({
                    "clients": [],
                    "decryption": "none",
                    "fallbacks": []
                }),
                "streamSettings": json.dumps({
                    "network": "tcp",
                    "security": "reality",
                    "externalProxy": [],
                    "realitySettings": {
                        "show": False,
                        "xver": 0,
                        "dest": f"{settings.MASK_HOST}:443",
                        "serverNames": [
                            settings.MASK_HOST,
                            f"www.{settings.MASK_HOST}"
                        ],
                        "privateKey": prvt_key,
                        "minClient": "",
                        "maxClient": "",
                        "maxTimediff": 0,
                        "shortIds": [
                            sid
                        ],
                        "settings": {
                            "publicKey": pubkey,
                            "fingerprint": "chrome",
                            "serverName": "",
                            "spiderX": "/"
                        }
                    },
                    "tcpSettings": {
                        "acceptProxyProtocol": False,
                        "header": {
                            "type": "none"
                        }
                    }
                }),
                "tag": "inbound-main",
                "sniffing": json.dumps({
                    "enabled": True,
                    "destOverride": [
                        "http",
                        "tls",
                        "quic",
                        "fakedns"
                    ],
                    "metadataOnly": False,
                    "routeOnly": False
                }),
                "clientStats": []
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url=cls.login_address, params=cls.params):
                    async with session.post(f'{cls.base_url}/add',
                                        json=data,
                                        headers=cls.json_headers) as response:
                        return await cls.check_response(response)

    @classmethod
    async def del_inbound(cls) -> bool:
        """ Удалить входящее соеденение """

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.post(f'{cls.base_url}/del/{settings.INBOUND_ID}') as response:
                    return await cls.check_response(response)

    @classmethod
    async def get_inbound(cls) -> bool|dict:
        """ Получить информацию о входящем соединении """

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.get(f'{cls.base_url}/get/{settings.INBOUND_ID}') as response:
                    if await cls.check_response(response):
                        return await response.json()
                    return False

    @classmethod
    async def add_client_to_inbound(
            cls,
            user_uuid: str,
            user_telegram_id: int|str,
            expiry_time: datetime|int,
            traffic_limit: int,
            inbound_id: int,
    ) -> bool:
        """ Добавить клиента """

        data = await cls.generate_data_for_user(user_uuid,
                                                user_telegram_id,
                                                expiry_time,
                                                traffic_limit,
                                                inbound_id)

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.post(
                        f'{cls.base_url}/addClient',
                        json=data,
                        headers=cls.json_headers
                ) as response:
                    return await cls.check_response(response)


    @classmethod
    async def get_client_from_inbound(cls, user_telegram_id: int) -> dict|bool:
        """ Получить инфо о клиенте """

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.get(f'{cls.base_url}/getClientTraffics/{user_telegram_id}') as response:
                    if await cls.check_response(response):
                        return await response.json()
                    return False


    @classmethod
    async def delete_client_from_inbound(cls, user_uuid: str) -> bool:
        """ Удалить клиента """

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.post(f'{cls.base_url}/{settings.INBOUND_ID}/delClient/{user_uuid}') as response:
                    return await cls.check_response(response)


    @classmethod
    async def update_client_expiry_time(cls,
                                        user_uuid: str,
                                        user_telegram_id: int,
                                        new_expiry_time: datetime,
                                        traffic_limit,
                                        inbound_id) -> bool:
        """ Обновить дату завершения подписки у клиента """

        data = await cls.generate_data_for_user(user_uuid,
                                                user_telegram_id,
                                                new_expiry_time,
                                                traffic_limit,
                                                inbound_id)

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.post(
                        f'{cls.base_url}/updateClient/{user_uuid}',
                        json=data,
                        headers=cls.json_headers
                ) as response:
                    return await cls.check_response(response)


    @classmethod
    async def get_client_traffics_with_email(cls, user_telegram_id: int) -> int:
        """ Возвращает трафик клиента по его email в байтах"""

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.get(f'{cls.base_url}/getClientTraffics/{user_telegram_id}') as response:
                    if await cls.check_response(response):
                        response = await response.json()
                        user_traffic = int(response['obj']['up']) + int(response['obj']['down'])
                        return user_traffic
                    return False


    @classmethod
    async def reset_clients_traffic(cls, user_telegram_id: int) -> bool:
        """ Сбросить трафик клиента """

        async with aiohttp.ClientSession() as session:
            async with session.post(url=cls.login_address, params=cls.params):
                async with session.post(f'{cls.base_url}/{settings.INBOUND_ID}/resetClientTraffic/{user_telegram_id}') as response:
                    return await cls.check_response(response)




if __name__ == '__main__':
    asyncio.run(PanelApi.add_inbound(settings.INBOUND_ID,
                                     settings.PROFILE_NAME,
                                     settings.INBOUND_PORT,
                                     settings.PRVTKEY,
                                     settings.SID,
                                     settings.PUBKEY))

    asyncio.run(PanelApi.add_client_to_inbound(settings.BRIDGE_UUID,
                                               'bridge',
                                               0,
                                               0,
                                               settings.INBOUND_ID))

    asyncio.run(PanelApi.add_inbound(settings.VIP_INBOUND_ID,
                                     settings.VIP_PROFILE_NAME,
                                     settings.VIP_INBOUND_PORT,
                                     settings.VIP_PRVTKEY,
                                     settings.VIP_SID,
                                     settings.VIP_PUBKEY))


