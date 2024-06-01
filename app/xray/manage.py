import asyncio
import subprocess
import json
import pprint
import uuid
from app.db.traffics.dao import TrafficsDAO

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# todo в конфиги
TRAFFIC_LIMIT = 200

# todo тестовые данные
TEST_DATA = {
    1: {'downlink': 6, 'uplink': 1234},
    2: {'downlink': 4234234, 'uplink': 4234234},
    3: {'downlink': 2342342, 'uplink': 234234},
    4: {'downlink': 234234234, 'uplink': 234234234}
}


class XrayManage:
    """Класс для взаимодействия с xray"""

    def __init__(self):
        # self.xray_config_path = '/usr/local/etc/xray/config.json'
        # todo в конфиги
        self.xray_config_path = '/home/lptpfila/PycharmProjects/vpn_manager/config.json'
        self.scheduler = AsyncIOScheduler()
        self.scheduler_job_id = None

    def add_user(self, user_id: int, new_uuid=None):
        """
        Добавляет пользователя в конфиг xray и перезагружает xray

        :param user_id:
        :param new_uuid:
        :return:
        """
        if not new_uuid:
            new_uuid = str(uuid.uuid4())

        new_user = {
            'email': user_id,
            'flow': 'xtls-rprx-vision',
            'id': new_uuid,
        }

        xray_config = self._read_config()

        for inbound in xray_config['inbounds']:
            if inbound['protocol'] == 'vless':
                clients_emails = [i['email'] for i in inbound['settings']['clients']]
                if user_id not in clients_emails:
                    inbound['settings']['clients'].append(new_user)

                    with open(self.xray_config_path, 'w') as file:
                        json.dump(xray_config, file, indent=4)
                    print(f'Профиль пользователя {user_id} добавлен в конфиг')
                    return new_uuid

        print(f'Профиль пользователя {user_id}, который вы пытаетесь добавить в конфиг уже существует')

    def del_user(self, user_id: int):
        """
        Удаляет пользователя из конфига xray и перезагружает xray

        :param user_id:
        :return:
        """
        xray_config = self._read_config()
        vless_inbound = [inbound for inbound in xray_config['inbounds'] if inbound['protocol'] == 'vless'][0]
        clients_profiles = [client_profile for client_profile in vless_inbound['settings']['clients']]

        for clients_profile in clients_profiles:
            if clients_profile['email'] == user_id:
                vless_inbound['settings']['clients'].remove(clients_profile)

                with open(self.xray_config_path, 'w') as file:
                    json.dump(xray_config, file, indent=4)
                print(f'Профиль пользователя {user_id} удален из конфига')
                return True

        print(f'Профиль пользователя {user_id}, который вы пытаетесь удалить из конфига не существует')
        return False

    @staticmethod
    def restart():
        """ Перезагружает xray

        :return:
        """
        command = ['systemctl', 'restart', 'xray']
        subprocess.run(command)
        print('xray успешно перезапущен')

    @staticmethod
    def read_all_stat():
        """ Читает статистику трафика всех соеденений """
        command = ['xray', 'api', 'statsquery']
        traffic = subprocess.run(command, stdout=subprocess.PIPE)
        traffic = traffic.stdout.decode('utf-8')
        traffic = json.loads(traffic)
        return traffic['stat']

    async def update_users_stats(self):
        """
        Обновляет статистику трафика в бд по всем пользователям и
        проверяет статистику на превышение лимита

        :return:
        """
        # xray_user_stats = self._read_users_stat()  # todo: раскоментить
        xray_user_stats = TEST_DATA
        print(1)
        db_user_stats = await TrafficsDAO().write_users_stat(xray_user_stats)
        print(2)
        overlimit_users = self._check_users_traffic(db_user_stats)
        print(f'Пользователи превышевшие лимит: {overlimit_users}')
        return db_user_stats

    def start_traffic_monitor(self):
        """
        Запуск мониторинга статистики пользователей

        :return:
        """
        print('Начали мониторинг')
        self.scheduler.add_job(self.update_users_stats, 'interval', seconds=10)
        self.scheduler_job_id = self.scheduler.start()

    def stop_traffic_monitor(self):
        """
        Остановка мониторинга статистики пользователей

        :return:
        """
        print('Остановили мониторинг')
        self.scheduler.remove_job(self.scheduler_job_id)

    @staticmethod
    async def _read_user_db_stat(user_id: int):
        """
        Прочитать из бд статистику трафика пользователя

        :param user_id:
        :return:
        """
        xray_user_stat = await TrafficsDAO().read_user_stat(user_id)
        xray_user_stat = xray_user_stat['downlink'] + xray_user_stat['uplink']
        xray_user_stat = round(xray_user_stat / 1024 ** 2, 2)
        print(f'{xray_user_stat} мб.')
        # return xray_user_stat

    @staticmethod
    def _check_users_traffic(users_stat: dict) -> list:
        """
        Проверить статистику трафика пользователей на превышение лимита

        :param users_stat:
        :return:
        """
        overlimit_users = []
        for user_id, user_stat in users_stat.items():
            if (user_stat['downlink'] + user_stat['uplink']) / 1024 ** 3 > TRAFFIC_LIMIT:
                overlimit_users.append(user_id)
        return overlimit_users

    @staticmethod
    def _read_users_stat() -> dict:
        """
        Сформировать dict из статистики трафика xray по пользователям на текущий момент

        :return:
        """
        users_stat = {}
        command = ['xray', 'api', 'statsquery']
        traffics = subprocess.run(command, stdout=subprocess.PIPE)
        traffics = traffics.stdout.decode('utf-8')
        traffics = json.loads(traffics)['stat']
        # traffics = filter(lambda x: 'user' in x['name'], traffics) todo: разкоментить

        for users_traffics in traffics:
            stat_line = users_traffics['name'].split('>>>')
            user_email = stat_line[1]
            traffic_type = stat_line[3]

            users_stat.setdefault(user_email, dict()).update({traffic_type: users_traffics['value']})
            # todo привести значения трафикак int

        return users_stat

    def _read_config(self):
        """
        Прочитать конфиг xray

        :return:
        """
        with open(self.xray_config_path, 'r') as file:
            xray_config = json.load(file)
            return xray_config


if __name__ == '__main__':
    a = XrayManage()


    # print(asyncio.run(a.read_user_stat(1)))
    # asyncio.run(a.update_users_stats(data))
    # asyncio.run(a.read_user_stat(data))
    # asyncio.run(a.update_users_stats())
    a.start_traffic_monitor()

    asyncio.sleep(15)

    # a.stop_traffic_monitor()

    asyncio.get_event_loop().run_forever()








