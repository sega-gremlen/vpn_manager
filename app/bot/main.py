from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers.user import *
from app.main_interface import main_interface
from app.bot.utils.jinja_templates import error_message, success_payment, xray_url, sub_renew_msg
from app.bot.handlers.admin import *
from app.bot.keyboards.inline import main_menu
from app.db.payment_requests.dao import PaymentRequestsDAO


bot = Bot(token=settings.BOT_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def send_error_msg(bott, telegram_id):
    await bott.send_message(telegram_id, text=error_message)


async def activate_subscription(payment_data, bott):
    payment_request: PaymentRequests = await PaymentRequestsDAO.find_one_or_none(
        label=payment_data['label']
    )
    telegram_id = payment_request.telegram_id

    # Создаём стейт что бы поменять состояния
    state = FSMContext(storage=MemoryStorage(),
                       key=StorageKey(chat_id=telegram_id, user_id=telegram_id, bot_id=bott.id))
    await state.set_state(BuySubSteps.SUB_ACTIVATED)

    raw_xray_url, sub_type = await main_interface.activate_subscription(payment_data)

    # Не знаю как это прокрутить в тесте
    if settings.MODE in ('PROD', 'DEV'):
        await bott.send_message(telegram_id,
                               text=success_payment.render(),
                               reply_markup=main_menu())

        if sub_type == 'first_time':
            await bott.send_message(telegram_id,
                                   text=xray_url.render(raw_xray_url),
                                   parse_mode=ParseMode.HTML)
            await bott.send_message(telegram_id,
                                   text=first_sub_activated_msg.render(),
                                   reply_markup=main_menu())
        else:
            await bott.send_message(telegram_id,
                                   text=sub_renew_msg.render(),
                                   reply_markup=main_menu())
    # Для тестов
    else:
        if raw_xray_url:
            return xray_url.render(raw_xray_url)

    # except Exception:
    #     print('asdf')
    #     await send_error_msg(bott, telegram_id)


# async def stop_bot(bot: Bot):
#     await bot.send_message(settings.ADMIN_ID, text='Бот остановлен')
#
#
# async def start_bot(bot: Bot):
#     await bot.send_message(settings.ADMIN_ID, text='Бот запущен')
#     # await set_general_commands(bot)
#     await set_admin_commands(bot)

# def bot_reply(message: Message):
#     await ret
#

dp = Dispatcher()


def register_user_handlers(dp: Dispatcher):

    # dp.message.register(get_start)
    # dp.message.register(admin.get_main_menu, F.from_user.id == settings.ADMIN_ID)
    # dp.message.register(user.get_main_menu, F.from_user.id != settings.ADMIN_ID)


    # Покупка подписки
    dp.callback_query.register(buy_subscription, F.data == 'buy_sub')
    dp.callback_query.register(get_main_menu, BuySubSteps.GET_PERIODS, F.data == 'back')
    dp.callback_query.register(buy_subscription_get_periods, BuySubSteps.GET_PERIODS)
    dp.callback_query.register(wait_for_payment, BuySubSteps.PAY_SUB, F.data == 'pay_url')
    dp.callback_query.register(buy_subscription, BuySubSteps.PAY_SUB, F.data == 'back')
    dp.callback_query.register(buy_subscription, BuySubSteps.TRIAL, F.data == 'back')
    dp.callback_query.register(activate_trial, BuySubSteps.TRIAL, F.data == 'activate_trial')
    dp.callback_query.register(get_main_menu, BuySubSteps.SUB_ACTIVATED, F.data == 'back')

    # Статистика подписки
    dp.callback_query.register(my_profile, F.data == 'my_profile')
    dp.callback_query.register(show_url_conf, MyProfile.GET_INSIDE, F.data == 'show_conf_url')
    dp.callback_query.register(my_profile, MyProfile.GET_URL, F.data == 'back')

    # Инструкции
    dp.callback_query.register(os_choose, F.data == 'instructions')
    dp.callback_query.register(os_choose, Instructions.OS_SECTION, F.data == 'back')
    # iOS
    dp.callback_query.register(ios_instruction, F.data == 'ios')
    dp.callback_query.register(ios_foxray_instruction, Instructions.OS_SECTION, F.data == 'foxray')
    dp.callback_query.register(ios_streisand_instruction, Instructions.OS_SECTION, F.data == 'streisand')
    dp.callback_query.register(ios_v2box_instruction, Instructions.OS_SECTION, F.data == 'v2box_ios')
    dp.callback_query.register(ios_instruction, Instructions.IOS_SECTION, F.data == 'back')
    # macOS
    dp.callback_query.register(macos_instruction, F.data == 'macos')
    dp.callback_query.register(macos_nekoray_instruction, Instructions.OS_SECTION, F.data == 'nekoray_mac')
    dp.callback_query.register(macos_v2box_instruction, Instructions.OS_SECTION, F.data == 'v2box_mac')
    dp.callback_query.register(macos_instruction, Instructions.MACOS_SECTION, F.data == 'back')
    # Android
    dp.callback_query.register(android_instruction, F.data == 'android')
    dp.callback_query.register(android_v2rayng_instruction, Instructions.OS_SECTION, F.data == 'v2rayng')
    dp.callback_query.register(android_nekobox_instruction, Instructions.OS_SECTION, F.data == 'nekobox')
    dp.callback_query.register(android_instruction, Instructions.ANDROID_SECTION, F.data == 'back')
    # Windows
    dp.callback_query.register(windows_instruction, F.data == 'windows')
    dp.callback_query.register(windows_nekoray_instruction, Instructions.OS_SECTION, F.data == 'nekoray_win')
    dp.callback_query.register(windows_invisible_man_instruction, Instructions.OS_SECTION, F.data == 'invisible_man')
    dp.callback_query.register(windows_instruction, Instructions.WINDOWS_SECTION, F.data == 'back')
    # Linux
    dp.callback_query.register(linux_instruction, F.data == 'linux')
    dp.callback_query.register(linux_nekoray_instruction, Instructions.OS_SECTION, F.data == 'nekoray_lin')
    dp.callback_query.register(windows_instruction, Instructions.LINUX_SECTION, F.data == 'back')

    # Чат с поддержкой

    # Старт/Главное меню
    dp.message.register(get_main_menu, CommandStart())
    dp.message.register(get_main_menu)
    dp.callback_query.register(get_main_menu, F.data == 'back')
    dp.callback_query.register(get_main_menu, F.data == 'main_menu')


    # Команды админа
    dp.message.register(refund_sub_enter, Command('refund_sub'))
    dp.message.register(refund_sub_get_url, Admin.REFUND_SUB)
    dp.message.register(add_user_get_tg_id, Command('add_user'))
    dp.message.register(add_user_main, Admin.ADD_USER)


register_user_handlers(dp)
