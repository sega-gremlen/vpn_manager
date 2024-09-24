import uuid
import hashlib
from datetime import timedelta

import requests

from app.db.dao.base import BaseDAO
from app.db.payment_requests.models import PaymentRequests
from app.db.payments.dao import PaymentsDAO

from app.db.users.dao import Users
from app.db.subscriptions.dao import SubscriptionsDAO, Subscriptions
from app.db.subscription_types.dao import SubscriptionTypes, SubscriptionTypesDAO
from app.db.payment_requests.dao import PaymentRequestsDAO
from app.aps import *

logger = logging.getLogger(__name__)


class MainInterface:
    """ Класс для управления приложением """

    @staticmethod
    async def create_user(telegram_id):
        """ Добавить пользователя в бд по его id в телеграме """

        user = await UsersDAO.find_one_or_none(telegram_id=telegram_id)

        if user is None:
            now_time = datetime.now()
            new_user = await UsersDAO.create(
                telegram_id=telegram_id,
                created_at=now_time,
                xray_uuid=str(uuid.uuid4()),
            )
            return new_user


    async def create_payment_request(self, telegram_id, sub_type: SubscriptionTypes):
        """ Создание в бд объекта запроса на оплату"""

        user: Users = await UsersDAO.find_one_or_none(telegram_id=telegram_id)
        amount = sub_type.price
        label = str(uuid.uuid4())
        created_at = datetime.now()
        stop_at = created_at + timedelta(seconds=settings.REDIRECT_URL_LIVING_TIME)
        periods = int(sub_type.duration / 30)
        redirect_url = self.__make_payment_url(amount, label)

        return await PaymentRequestsDAO.create(
            user_id=user.id,
            telegram_id=telegram_id,
            label=label,
            created_at=created_at,
            stop_at=stop_at,
            periods=periods,
            subscription_type_id=sub_type.id,
            redirect_url=redirect_url
        )

    @staticmethod
    async def create_subscription(user_id, subscription_type_id, start, stop):
        return await SubscriptionsDAO.create(
            user_id=user_id,
            subscription_type_id=subscription_type_id,
            start=start,
            stop=stop,
        )

    @staticmethod
    async def create_periods(start_date, sub_id, periods_value, trial=False):

        if trial:
            trial_sub_type: SubscriptionTypes = await SubscriptionTypesDAO.find_one_or_none(name='trial')
            delta = trial_sub_type.duration
        else:
            delta = 30

        first_period = await PeriodsDAO.create(
            subscription_id=sub_id,
            start=start_date,
            stop=start_date + timedelta(days=delta),
        )

        relative_period = first_period

        for period in range(int(periods_value) - 1):
            start = relative_period.stop
            stop = relative_period.stop + timedelta(days=delta)
            relative_period = await PeriodsDAO.create(
                subscription_id=sub_id,
                start=start,
                stop=stop,
            )


    @staticmethod
    async def create_payment(subscription_id, user_id, created_at, payment_data):
        await PaymentsDAO.create(
            subscription_id=subscription_id,
            user_id=user_id,
            created_at=created_at,

            # Параметры api yoomoney
            notification_type=payment_data['notification_type'],
            operation_id=payment_data['operation_id'],
            operation_label=payment_data['operation_label'],
            amount=float(payment_data['amount']),
            withdraw_amount=float(payment_data['withdraw_amount']),
            currency=int(payment_data['currency']),
            api_datetime=datetime.strptime(payment_data['datetime'], "%Y-%m-%dT%H:%M:%SZ"),
            sender=payment_data['sender'],
            label=payment_data['label'],
            sha1_hash=payment_data['sha1_hash'],
            unaccepted=True if payment_data['unaccepted'] == 'true' else False,
        )


    async def activate_trial_subscription(self, telegram_id):
        """ Активируем пробную подписку и генерируем url-config """

        user = await UsersDAO.find_one_or_none(telegram_id=telegram_id)
        sub_type = await SubscriptionTypesDAO.find_one_or_none(name='trial')
        dt_now = datetime.now()
        stop = dt_now + timedelta(days=sub_type.duration)

        # Создаём запись с подпиской
        subscription: Subscriptions = await self.create_subscription(
            user.id,
            sub_type.id,
            dt_now,
            stop,
        )

        # Создаём период для подсчета трафика в месяц
        await self.create_periods(dt_now, subscription.id,
                                  1,
                                  trial=True)

        # Добавляем юзера в панель
        await PanelApi.add_client_to_inbound(user.xray_uuid,
                                             user.telegram_id,
                                             subscription.stop,
                                             settings.TRAFFIC_LIMIT * 1024 ** 3)

        # Меняем статус потраченного пробного периода
        await BaseDAO.patch(user, trial_wasted=True)

        # Делаем данные url для клиента
        xray_client_config_url = await self.render_xray_url(user.xray_uuid)

        return xray_client_config_url


    async def activate_subscription(self, payment_data: dict):
        """ Активируем/продливаем обычную подписку и генерируем url-config

        Если переходим с пробной на платную, делаем:
        - сброс трафика в день оформления платной
        - смещаем в бд дату конца подписки пробной
        - смещаем в бд дату конца периода пробной подписки

        first_time - подписка оформляется в первый раз

        renew - подписка существует на данный момент и просто продливается

        again - пользователь оформил подписку спустя время после окончания предыдущей

        """
        logger.info('13')
        sub_activation_types = ('first_time', 'renew')
        sub_activation_type = sub_activation_types[1]
        last_sub_type_name = None

        dt_now = datetime.now()
        payment_request: PaymentRequests = await PaymentRequestsDAO.find_one_or_none(label=payment_data['label'])

        # Проверка на то что подписка оформляется первый раз
        last_sub: Subscriptions = await SubscriptionsDAO.find_last_sub_by_user_tg_id(payment_request.telegram_id)
        if last_sub:
            last_sub_type_name = await SubscriptionTypesDAO.find_one_or_none(id=last_sub.subscription_type_id)
            last_sub_type_name = last_sub_type_name.name
        else:
            sub_activation_type = sub_activation_types[0]

        # Если оплатил пользователь с активной на данный момент подпиской
        if last_sub and last_sub.stop >= dt_now:
            logger.info('14')
            # Если эта подписка не пробная
            if last_sub_type_name != 'trial':
                logger.info('15')
                start_date_for_periods = last_sub.stop
                stop = last_sub.stop + timedelta(days=payment_request.periods * 30)
                # Сдвигаем дату окончания подписки в бд
                await BaseDAO.patch(last_sub, stop=stop)
                subscription = last_sub
                sub_activation_type = sub_activation_types[1]
                # Обновляем дату окончания в работе
                await update_traffic_reset_job_date(payment_request.telegram_id, stop)
            # Если эта подписка пробная
            else:
                logger.info('16')
                # Сброс трафика в день оформления платной
                await PanelApi.reset_clients_traffic(payment_request.telegram_id)
                # Смещаем назад в бд дату конца подписки пробной
                await BaseDAO.patch(last_sub, stop=dt_now)
                # Смещаем назад в бд дату конца периода пробной подписки
                period = await PeriodsDAO.find_one_or_none(subscription_id=last_sub.id)
                await BaseDAO.patch(period, stop=dt_now)
                # Создаём запись с платной подпиской
                subscription: Subscriptions = await self.create_subscription(
                    payment_request.user_id,
                    payment_request.subscription_type_id,
                    dt_now,
                    dt_now + timedelta(days=payment_request.periods * 30),
                )
                start_date_for_periods = subscription.start

                logger.info('16.1')
                # Добавляем работу по сбросу трафика
                await add_traffic_reset_job(payment_request.telegram_id,
                                                  subscription.start,
                                                  subscription.stop,
                                                  30)

        # Если оплатил пользователь с неактивной на данный момент подпиской
        else:
            logger.info('17')
            # Создаём запись с платной подпиской
            subscription: Subscriptions = await self.create_subscription(
                payment_request.user_id,
                payment_request.subscription_type_id,
                dt_now,
                dt_now + timedelta(days=payment_request.periods * 30),
            )
            start_date_for_periods = subscription.start
            logger.info('18')
            # Добавляем работу по сбросу трафика
            await add_traffic_reset_job(payment_request.telegram_id,
                                            subscription.start,
                                            subscription.stop,
                                            30)

        logger.info('19')

        # Создаём периоды для подсчета трафика в месяц
        await self.create_periods(start_date_for_periods, subscription.id, payment_request.periods)

        # Создаём запись об оплате
        await self.create_payment(subscription.id, payment_request.user_id, dt_now, payment_data)

        # Меняем статус оплаты
        await BaseDAO.patch(payment_request, completed=True)

        user: Users = await UsersDAO.find_one_or_none(telegram_id=payment_request.telegram_id)
        if sub_activation_type == 'first_time':

            # Добавляем юзера в панель
            await PanelApi.add_client_to_inbound(user.xray_uuid,
                                                 user.telegram_id,
                                                 subscription.stop,
                                                 settings.TRAFFIC_LIMIT * 1024 ** 3)

            # Меняем статус потраченного пробного периода
            await BaseDAO.patch(user, trial_wasted=True)

            # Делаем url для клиента
            xray_client_config_url = await self.render_xray_url(user.xray_uuid)

        else:
            # Обновляем дату окончания подписки юзера в панель
            await PanelApi.update_client_expiry_time(user.xray_uuid,
                                                     user.telegram_id,
                                                     subscription.stop,
                                                     settings.TRAFFIC_LIMIT * 1000 ** 3)

            xray_client_config_url = None

        return xray_client_config_url, sub_activation_type


    @staticmethod
    async def get_active_subscription(telegram_id):
        """ Проверяем наличие активной подписки у юзера """

        last_sub: Subscriptions = await SubscriptionsDAO.find_last_sub_by_user_tg_id(telegram_id)

        if last_sub and last_sub.stop >= datetime.now():
            return last_sub


    @staticmethod
    async def render_xray_url(xray_uuid):
        """ Генерация данных для создания конфигурационного url """

        xray_url_data = {
            'xray_uuid': xray_uuid,
            'host': settings.MAIN_HOST,
            'port': settings.INBOUND_PORT,
            'pbk': settings.PUBKEY,
            'mask_host': settings.MASK_HOST,
            'sid': settings.SID,
            'profile_name': settings.PROFILE_NAME,
        }

        return xray_url_data


    @staticmethod
    def generate_hash(string_to_hash: str) -> str:
        """ Сгенерировать хэш сумму из строки """

        generated_hash = hashlib.sha1()
        generated_hash.update(string_to_hash.encode('utf-8'))
        generated_hash = generated_hash.hexdigest()
        return generated_hash


    def check_hash(self, data_to_check):
        """ Проверка хэша api-уведомления

        Пример строки которая проверяется на хэш-сумму
        notification_type&operation_id&amount&currency&datetime&sender&codepro&notification_secret&label
        card-incoming&762548246564417096&77.60&643&2024-08-16T21:17:55Z&&false&RyrJP/v4ornHDNAd8hpKmJS1&
        3e2be2ac-8771-4923-bbad-125940a6d9df
        """

        sha_input = (
            f'{data_to_check["notification_type"]}&'
            f'{data_to_check["operation_id"]}&'
            f'{data_to_check["amount"]}&'
            f'{data_to_check["currency"]}&'
            f'{data_to_check["datetime"]}&'
            f'{data_to_check["sender"]}&'
            f'{data_to_check["codepro"]}&'
            f'{settings.NOTI_SECRET}&'
            f'{data_to_check["label"]}'
        )

        print('Проверяем', sha_input)

        if self.generate_hash(sha_input) == data_to_check['sha1_hash']:
            return True
        return False


    @staticmethod
    async def create_redirect_url(label):
        """ Сформировать редирект ссылку """

        redirect_url = f'http://{settings.NOTI_HOST}:{settings.NOTI_PORT}/redirect/{label}'
        return redirect_url

    @staticmethod
    def __make_payment_url(amount, label):
        """ Сформировать ссылку на оплату в ЮMoney """

        main_url = 'https://yoomoney.ru/quickpay/confirm'
        receiver = settings.RECIEVER
        quickpay_form = 'button'
        payment_type = 'AC'

        payment_url = (
            f'{main_url}/?receiver={receiver}&'
            f'quickpay-form={quickpay_form}&'
            f'paymentType={payment_type}&'
            f'sum={amount}&'
            f'label={label}'
        )

        return payment_url

    @staticmethod
    async def get_user_stat(user_telegram_id: int) -> dict:
        """ Для выдачи статистики по подписке в бот """

        # Выдаёт join таблицы: Periods, Subscriptions
        curr_period_and_sub = await PeriodsDAO.find_current_period_sub(user_telegram_id)
        user_traffic = round(await PanelApi.get_client_traffics_with_email(user_telegram_id) / 1024 ** 3, 2)

        sub_created_at = curr_period_and_sub.start_1.strftime('%d.%m.%Y %H:%M:%S') + ' МСК'
        sub_end_datetime = curr_period_and_sub.stop_1.strftime('%d.%m.%Y %H:%M:%S') + ' МСК'

        job = scheduler.get_job(f'trf_reset_{user_telegram_id}')
        if job:
            next_traffic_reset = job.next_run_time.strftime("%d.%m.%Y %H:%M:%S") + ' МСК'
        else:
            next_traffic_reset = 'Нет сброса трафика'

        days_to_end: timedelta = (curr_period_and_sub.stop_1 - curr_period_and_sub.start_1).days

        context = {
            "telegram_id": user_telegram_id,
            "sub_created_at": sub_created_at,
            "sub_end_datetime": sub_end_datetime,
            "period_value": user_traffic,
            "traffic_limit": settings.TRAFFIC_LIMIT,
            "next_traffic_reset": next_traffic_reset,
            "days_to_end": days_to_end,
        }

        return context

    @staticmethod
    async def get_latest_github_release(program_name):
        pockets_data= {
            'windows_invisible_man': (
                'https://api.github.com/repos/InvisibleManVPN/InvisibleMan-XRayClient/releases/latest',
                'InvisibleManXRay-x64.zip'
            ),
            'windows_nekoray': (
                'https://api.github.com/repos/MatsuriDayo/nekoray/releases/latest',
                'windows64.zip'
            ),
            'android_v2rayNG': (
                'https://api.github.com/repos/2dust/v2rayNG/releases/latest',
                'universal.apk'
            ),
            'android_nekobox': (
                'https://api.github.com/repos/MatsuriDayo/NekoBoxForAndroid/releases/latest',
                'arm64'
            ),
            'macos_nekoray_intel': (
                'https://api.github.com/repos/abbasnaqdi/nekoray-macos/releases/latest',
                'intel-chip-official.zip'
            ),
            'macos_nekoray_apple': (
                'https://api.github.com/repos/abbasnaqdi/nekoray-macos/releases/latest',
                'apple-chip-official.zip'
            ),
        }

        url = pockets_data[program_name][0]
        asset_str = pockets_data[program_name][1]

        response = requests.get(url)
        for release in response.json()['assets']:
            if asset_str in release['name']:
                return release['browser_download_url']



main_interface = MainInterface()
