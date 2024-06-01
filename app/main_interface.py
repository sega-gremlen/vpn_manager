import asyncio
import uuid
from datetime import datetime, timedelta, date

from settings import MY_HOSTING, REDIRECT_URL_LIVING_TIME

from app.db.traffics.dao import TrafficsDAO
from app.db.users.dao import UsersDAO, Users
from app.db.subscriptions.dao import SubscriptionsDAO, Subscriptions
from app.db.subscribe_types.dao import SubscriptionTypesDAO, SubscriptionTypes
from app.db.payments.dao import PaymentsDAO
from app.db.payment_requests.dao import PaymentRequestsDAO

from app.xray.manage import XrayManage


class MainInterface:
    @staticmethod
    async def create_user(telegram_id):
        user = await UsersDAO.find_one_or_none(telegram_id=telegram_id)

        if user is None:
            now_time = datetime.now()
            new_user = await UsersDAO.create(
                telegram_id=telegram_id,
                created_at=now_time,
            )
            return new_user

    @staticmethod
    async def assign_xray_uuid_to_user(telegram_id):
        user: UsersDAO = await UsersDAO.find_one_or_none(telegram_id=telegram_id)
        xray_uuid = XrayManage().add_user(telegram_id)
        await user.patch_some(xray_uuid=xray_uuid)
        return xray_uuid

    @staticmethod
    async def create_subscription(
            telegram_id,
            period,
            subscribe_type,
            payment_label,
            last_active_subscription: Subscriptions = None,
    ):
        datetime_now = datetime.now()
        user: Users = await UsersDAO.find_one_or_none(telegram_id=telegram_id)
        print(user)

        # Если уже есть действующая подписка
        if last_active_subscription:
            start = last_active_subscription.stop + timedelta(days=1)
        else:
            start = date.today()

        stop = start + timedelta(days=period * 30)

        new_subscription = await SubscriptionsDAO.create(
            created_at=datetime_now,
            start=start,
            stop=stop,
            user_id=user.id,
            subscription_type=subscribe_type,
            payment_label=payment_label
        )

        return new_subscription

    async def check_existing_sub(self, telegram_id):
        """Проверяем наличие и статус активности подписки у существующего юзера"""

        user = await UsersDAO.find_one_or_none(telegram_id=telegram_id)

        if user:
            last_active_subscription = await self.__find_last_active_subscription(user)
            return last_active_subscription

    async def create_payment_request(self, telegram_id, periods, sub_type_name):
        """ Создание объекта редирект ссылки - запроса на оплату"""

        user: Users = await UsersDAO.find_one_or_none(telegram_id=telegram_id)
        sub_type = await SubscriptionTypesDAO.find_one_or_none(name=sub_type_name)
        amount = periods * sub_type.price
        label = str(uuid.uuid4())
        created_at = datetime.now()
        stop_at = created_at + timedelta(seconds=REDIRECT_URL_LIVING_TIME)

        return await PaymentRequestsDAO.create(
            user_id=user.id,
            telegram_id=telegram_id,
            label=label,
            created_at=created_at,
            stop_at=stop_at,
            periods=periods,
            subscription_type=sub_type_name,
            redirect_url=self.__make_payment_url(amount, label)
        )

    @staticmethod
    async def create_redirect_url(label):
        redirect_url = f'{MY_HOSTING}/redirect/{label}'
        return redirect_url

    @staticmethod
    async def check_payment_request_for_relevance(payment_request):
        last_payment_request = PaymentRequestsDAO.find_last_payment_request()



    @staticmethod
    async def __find_last_active_subscription(user: Users):

        #todo Сделать проверку подписки на то что она оплачена, если не оплачена подписка не счиатается активной
        subscription = await SubscriptionsDAO.find_all_by_filter(user_id=user.id)
        if subscription:
            subscription = subscription[-1]
            if date.today() <= subscription.stop:
                return subscription

    @staticmethod
    def __make_payment_url(amount, label):
        main_url = 'https://yoomoney.ru/quickpay/confirm'
        receiver = 4100118561425598  # todo в окружение
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
    def __write_traffic():
        users_traffic = XrayManage().read_users_stat()
        for user_traffic in users_traffic:
            print(user_traffic)

    def watch_user_stat(self, tg_id):
        ...

    def start_monitor(self):
        ...


if __name__ == '__main__':
    async def test():
        # print(await MainInterface().create_redirect_url('0efd2651-e5be-48d1-a052-fc4ab043168a'))

        await MainInterface().create_payment_request('741614077',
                                                     1,
                                                     'simple',
                                                     date.today(),
                                                     date.today() + timedelta(days=30))

    asyncio.run(test())
