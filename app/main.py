import asyncio
import logging

from app.bot.main import bot, dp
from app.bot.utils.commands import set_commands
from app.aps import aps


async def start():
    try:
        logging.basicConfig(level=logging.INFO)
        aps.scheduler.start()
        await aps.add_traffic_monitor_job()
        await dp.start_polling(bot)
        await set_commands(bot)
    finally:
        await bot.session.close()
        aps.scheduler.shutdown()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start())