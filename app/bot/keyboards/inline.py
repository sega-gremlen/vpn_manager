from aiogram.utils.keyboard import InlineKeyboardBuilder


from app.db.subscription_types.models import SubscriptionTypes
from config import settings


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
    keyword_builder.button(text='Чат с поддержкой', url=settings.SUPPORT_ID)
    keyword_builder.button(text='Повторить попытку', callback_data='repeat')
    keyword_builder.button(text='Главное меню', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def user_main_menu_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Купить подписку', callback_data='buy_sub')
    keyword_builder.button(text='Мой профиль', callback_data='my_profile')
    keyword_builder.button(text='Инструкции', callback_data='instructions')
    keyword_builder.button(text='Чат с техподдержкой', url=settings.SUPPORT_ID)
    keyword_builder.adjust(1, 1, 1, 1, 1)
    return keyword_builder.as_markup()


def admin_main_menu_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Добавить пользователя', callback_data='add_user')
    keyword_builder.button(text='Приостановить подписку', callback_data='suspend_user')
    keyword_builder.button(text='Удалить пользователя', callback_data='del_user')
    keyword_builder.adjust(1, 1, 1)
    return keyword_builder.as_markup()


def periods_value_kb(sub_params, trial_wasted):
    """
    i.name, i.price, i.duration
    """
    keyword_builder = InlineKeyboardBuilder()
    for params in sub_params[:-1]:
        periods = int(params[2] / 30)
        keyword_builder.button(text=f'Месяцев: {periods} | {params[1]}р.', callback_data=params[0])
    if not trial_wasted:
        keyword_builder.button(text=f'Пробный период - {sub_params[-1][2]} дней  | бесплатно', callback_data='trial')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def pay_kb(sub_type: SubscriptionTypes, pay_url):
    keyword_builder = InlineKeyboardBuilder()
    periods = int(sub_type.duration / 30)
    keyword_builder.button(text=f'Оплатить {periods} мес./{sub_type.price}р.',
                           callback_data='pay_url',
                           url=pay_url,
                           )
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def profile_stat_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Моя ключ-ссылка', callback_data='show_conf_url')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def activate_trial_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Да, поехали!', callback_data='activate_trial')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def os_choose_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='iOS', callback_data='ios')
    keyword_builder.button(text='macOS', callback_data='macos')
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
    keyword_builder.button(text='V2Box', callback_data='v2box_ios')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def macos_choose_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='NekoRay', callback_data='nekoray_mac')
    keyword_builder.button(text='V2Box', callback_data='v2box_mac')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def android_choose_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='v2rayNG', callback_data='v2rayng')
    keyword_builder.button(text='Nekobox', callback_data='nekobox')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def windows_choose_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Nekoray', callback_data='nekoray_win')
    keyword_builder.button(text='Invisible Man', callback_data='invisible_man')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def linux_choose_kb():
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='Nekoray', callback_data='nekoray_lin')
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def download_windows_invisible_man(download_url):
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='🔽 Скачать(.zip) 🔽',
                           url=download_url)
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def download_windows_nekoray(download_url):
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='🔽 Скачать(.zip) 🔽',
                           url=download_url)
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def download_android_v2rayNG(download_url):
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='🔽 Скачать(.apk) 🔽',
                           url=download_url)
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def download_android_nekobox(download_url):
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='🔽 Скачать(.apk) 🔽',
                           url=download_url)
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()


def download_macos_nekoray(download_url_intel, download_url_apple):
    keyword_builder = InlineKeyboardBuilder()
    keyword_builder.button(text='🔽 Скачать для процессоров intel (.zip) 🔽',
                           url=download_url_intel)
    keyword_builder.button(text='🔽 Скачать для процессоров apple (.zip) 🔽',
                           url=download_url_apple)
    keyword_builder.button(text='Назад', callback_data='back')
    keyword_builder.adjust(1)
    return keyword_builder.as_markup()
