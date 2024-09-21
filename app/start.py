import asyncio
import logging

from app.bot.main import bot, dp
from app.aps import start_scheduler
from app.bot.utils.commands import set_commands


async def start():
    try:
        logging.basicConfig(level=logging.INFO)
        await start_scheduler()
        await set_commands(bot)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())