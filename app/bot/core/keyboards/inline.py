from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# from app.bot.core.utils.callbackdata import BuySubscription


def copy_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Копировать', callback_data='back')
    keyword_builder.adjust(1)

    return keyword_builder.as_markup()


def back_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def main_menu():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Главное меню', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def support_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Чат с поддержкой', url='https://t.me/P1xelman')
    keyword_builder.button(text='Повторить попытку', callback_data='repeat')
    keyword_builder.button(text='Главное меню', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def user_main_menu_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Купить подписку', callback_data='buy_sub')
    keyword_builder.button(text='У меня подписка с прошлого VPN', callback_data='existing_sub')
    keyword_builder.button(text='Мой профиль', callback_data='my_sub')
    keyword_builder.button(text='Инструкции', callback_data='instructions')
    keyword_builder.button(text='Чат с техподдержкой', url='https://t.me/P1xelman')

    keyword_builder.adjust(1, 1, 1, 1, 1)

    return keyword_builder.as_markup()


def admin_main_menu_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Добавить пользователя', callback_data='add_user')
    keyword_builder.button(text='Приостановить подписку', callback_data='suspend_user')
    keyword_builder.button(text='Удалить пользователя', callback_data='del_user')

    keyword_builder.adjust(1, 1, 1)

    return keyword_builder.as_markup()


def periods_value_kb():
    keyword_builder = InlineKeyboardBuilder()

    keyword_builder.button(text='1 месяц: 50р.', callback_data='1')
    keyword_builder.button(text='6 месяцев: 300р.', callback_data='6')
    keyword_builder.button(text='12 месяцев: 600р.', callback_data='12')
    keyword_builder.button(text='Назад', callback_data='back')

    keyword_builder.adjust(1)

    return keyword_builder.as_markup()


def pay_kb(periods, pay_url):
    keyword_builder = InlineKeyboardBuilder()

    keyword_builder.button(text=f'Оплатить {periods} мес./{periods * 50}р.',
                           callback_data='pay_url',
                           url=pay_url,
                           )

    keyword_builder.button(text='Назад', callback_data='back')

    keyword_builder.adjust(1)

    return keyword_builder.as_markup()


def os_choose_kb():
    keyword_builder = InlineKeyboardBuilder()

    keyword_builder.button(text='iOS', callback_data='ios')
    keyword_builder.button(text='Android', callback_data='android')
    keyword_builder.button(text='Windows', callback_data='windows')
    keyword_builder.button(text='Linux', callback_data='linux')
    keyword_builder.button(text='Назад', callback_data='back')

    keyword_builder.adjust(1)

    return keyword_builder.as_markup()


def ios_choose_kb():
    keyword_builder = InlineKeyboardBuilder()

    keyword_builder.button(text='foXray', callback_data='foxray')
    keyword_builder.button(text='Streisand', callback_data='streisand')
    keyword_builder.button(text='Назад', callback_data='back')

    keyword_builder.adjust(1)

    return keyword_builder.as_markup()
