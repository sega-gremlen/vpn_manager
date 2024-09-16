import asyncio
import logging

from app.bot.main import bot, dp
from app.bot.utils.commands import set_commands
from app.aps import start_scheduler


async def start():
    try:
        logging.basicConfig(level=logging.INFO)
        await start_scheduler()
        await dp.start_polling(bot)
        await set_commands(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())