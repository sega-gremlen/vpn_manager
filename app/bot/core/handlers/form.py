from aiogram.types import Message
from aiogram.fsm.context import FSMContext


from app.bot.templates.jinja_templates import buy_subscription_tm
from app.bot.core.utils.statesform import BuySubSteps


async def get_form(message: Message, state: FSMContext):
    await message.answer(f'Вы ввели: {message.text}')
    # await message.answer(buy_subscription_tm.render())
    await state.set_state(BuySubSteps.GET_PERIODS)


async def get_periods(message: Message):
    await message.answer(f'Вы ввели: {message.text}')

