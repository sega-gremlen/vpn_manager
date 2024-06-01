from settings import settings

from aiogram import Bot

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeAllChatAdministrators


async def set_general_commands(bot: Bot):
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

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def set_admin_commands(bot: Bot):
    commands = [
        BotCommand(
            command='add_user',
            description='Добавить пользователя',
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeAllChatAdministrators())

#FBoYLJBK6hGEn2QwiUS6utmCRFT8GVShoFuKKrcXxQgo
#FBoYLJBK6hGEn2QwiUS6utmCRFT8GVShoFuKKrcXxQgo