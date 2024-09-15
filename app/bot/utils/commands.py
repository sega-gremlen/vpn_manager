from config import settings

from aiogram import Bot
from aiogram.types import BotCommandScopeChatAdministrators, BotCommandScopeDefault, BotCommand, BotCommandScopeChat

from aiogram.types import BotCommand


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Начать работу'
        ),
        BotCommand(
            command='info',
            description='Информация о проекте',
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
        )

    ]


    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=settings.ADMIN_ID))

