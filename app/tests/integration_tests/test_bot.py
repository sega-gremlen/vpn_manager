from unittest.mock import AsyncMock

from aiogram.fsm.context import FSMContext

from app.bot.handlers.user import get_main_menu
from app.bot.keyboards.inline import user_main_menu_kb
from app.bot.main import send_error_msg
from app.bot.utils.jinja_templates import user_main_menu_tm


async def test_get_main_menu(memory_storage, storage_key):
    message = AsyncMock()
    state = FSMContext(
        storage=memory_storage,
        key=storage_key
    )
    await get_main_menu(message, state)
    message.answer.assert_awaited_with(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())


async def test_send_error_msg(bot):
    await send_error_msg(bot, 1000000000)
