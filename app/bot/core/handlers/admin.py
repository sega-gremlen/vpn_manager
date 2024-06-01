from aiogram import Bot
from aiogram.types import Message
from ..keyboards.inline import admin_main_menu_kb


async def get_main_menu(message: Message):
    await message.answer(text='Админ панель', reply_markup=admin_main_menu_kb())
