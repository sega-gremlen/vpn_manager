import asyncio
import logging

from app.bot.core.utils.statesform import BuySubSteps
from settings import settings

from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from app.bot.core.utils.commands import set_general_commands, set_admin_commands
from app.bot.core.handlers import admin, user
from aiogram.filters import CommandStart, Command, state
from aiogram.types import Message
from app.bot.core.handlers.callback import *
from app.bot.core.handlers import form
from app.bot.core.utils.statesform import BuySubSteps, CheckExistingSub, ChooseOS

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


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


async def main():
    dp = Dispatcher()

    # dp.message.register(get_start)
    # dp.message.register(admin.get_main_menu, F.from_user.id == settings.ADMIN_ID)
    # dp.message.register(user.get_main_menu, F.from_user.id != settings.ADMIN_ID)

    # Покупка подписки
    dp.callback_query.register(buy_subscription, F.data == 'buy_sub')
    dp.callback_query.register(get_main_menu, BuySubSteps.GET_PERIODS, F.data == 'back')
    dp.callback_query.register(buy_subscription_get_periods, BuySubSteps.GET_PERIODS)
    dp.callback_query.register(wait_for_payment, BuySubSteps.PAY_SUB, F.data == 'pay_url')
    dp.callback_query.register(buy_subscription, BuySubSteps.PAY_SUB, F.data == 'back')

    # Проверка на подписку в старом VPN
    dp.callback_query.register(existing_sub, F.data == 'existing_sub')
    dp.message.register(existing_sub_number_check, CheckExistingSub.GET_NUMBER, F.text.regexp(r'^\+7\d{10}$'))
    dp.callback_query.register(existing_sub, CheckExistingSub.GET_NUMBER, F.data == 'repeat')
    dp.message.register(wrong_number_format, CheckExistingSub.GET_NUMBER)

    # Стата текущей подписки

    # Инструкции
    dp.callback_query.register(os_choose, F.data == 'instructions')
    dp.callback_query.register(os_choose, ChooseOS.OS_SECTION, F.data == 'back')
    dp.callback_query.register(ios_instruction, F.data == 'ios')
    dp.callback_query.register(foxray_instruction, F.data == 'foxray')
    dp.callback_query.register(streisand_instruction, F.data == 'streisand')
    dp.callback_query.register(ios_instruction, ChooseOS.PROGRAM_SECTION, F.data == 'back')
    dp.callback_query.register(android_instruction, F.data == 'android')
    dp.callback_query.register(windows_instruction, F.data == 'windows')
    dp.callback_query.register(linux_instruction, F.data == 'linux')


    # Чат с поддержкой

    # Старт/Главное меню
    dp.message.register(get_main_menu, CommandStart())
    dp.callback_query.register(get_main_menu, F.data == 'back')
    dp.callback_query.register(get_main_menu, F.data == 'main_menu')



    # dp.startup.register(start_bot)
    # dp.shutdown.register(stop_bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
