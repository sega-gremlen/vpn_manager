from config import settings

from aiogram import Bot
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat

from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Начать работу'
        ),
    ]

    admin_commands = commands + [
        BotCommand(
            command='add_user',
            description='Добавить пользователя вручную',
        ),
        BotCommand(
            command='refund_sub',
            description='Возврат денег'
        ),
        BotCommand(
            command='curr_jobs',
            description='Текущие работы aps'
        ),
        BotCommand(
            command='trf_rst',
            description='Принудительный сброс трафика'
        )
    ]


    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=settings.ADMIN_ID))
