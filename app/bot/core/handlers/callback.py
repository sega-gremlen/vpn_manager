import asyncio
from datetime import date, timedelta
from typing import List

from app.bot.core.main import Bot

from aiogram.types import CallbackQuery, Message, InputMedia
from app.bot.core.utils.statesform import BuySubSteps, CheckExistingSub, ChooseOS
from app.bot.templates.jinja_templates import *
from aiogram.fsm.context import FSMContext
from app.bot.core.keyboards.inline import *
from app.db.old_vpn_db.requests import check_clients_number, Client
from app.bot.sources.source_urls import *

from app.db.payment_requests.models import PaymentRequests
from app.db.subscriptions.models import Subscriptions
from app.db.users.models import Users

from app.main_interface import MainInterface


# -------------------- Оформление новой подписки --------------------
async def get_main_menu(message: Message, state: FSMContext):
    print('Запущен хэндлер get_main_menu')

    await state.clear()

    if type(message) is CallbackQuery:
        await message.message.edit_text(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())
    else:
        if message.text.startswith('/'):
            await MainInterface().create_user(telegram_id=str(message.from_user.id))

            await message.answer(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())
        else:
            await message.edit_text(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())


async def buy_subscription(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер buy_subscription')
    await call.message.edit_text(buy_subscription_tm.render(), reply_markup=periods_value_kb())
    await state.clear()
    await state.update_data(user_id=call.message.from_user.id)
    await state.set_state(BuySubSteps.GET_PERIODS)
    await call.answer()


async def buy_subscription_get_periods(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер buy_subscription_get_periods')

    periods = int(call.data)
    telegram_id = str(call.from_user.id)

    last_active_sub: Subscriptions = await MainInterface().check_existing_sub(telegram_id)

    if last_active_sub:
        stop_date = (last_active_sub.stop + timedelta(days=30 * periods))
        text = (f'С учетом уже существующей подписки активной до {last_active_sub.stop}, '
                f'подписка будет продлена до {stop_date.strftime("%d.%m.%Y")} включительно')
    else:
        stop_date = (date.today() + timedelta(days=30 * periods))
        text = f'Подписка будет активна до {stop_date.strftime("%d.%m.%Y")} включительно'

    payment_request: PaymentRequests = await MainInterface().create_payment_request(
        telegram_id,
        periods,
        'simple',
    )

    redirect_url = await MainInterface().create_redirect_url(payment_request.label)

    await call.message.edit_text(text=text, reply_markup=pay_kb(periods, redirect_url))

    await state.set_state(BuySubSteps.PAY_SUB)
    await state.update_data(telegram_id=telegram_id)

    await call.answer()


async def wait_for_payment(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер wait_for_payment')

    await call.message.answer('Ждём подтверждения оплаты...')

    # data = await state.get_data()
    #
    # a = await bot.send_message(data['telegram_id'], )
    #
    # print(a)
    #
    # await state.update_data(last_call=call)


# -------------------- Подписка со старого VPN --------------------
async def existing_sub(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер get_exist_sub')

    await state.set_state(CheckExistingSub.GET_NUMBER)
    await call.message.edit_text('Введите номер телефона в формате: +70007770077', reply_markup=back_kb())
    await call.answer()


async def existing_sub_number_check(message: Message):
    phone_to_check = message.text
    clients: List[Client] = check_clients_number(phone_to_check)

    if len(clients) == 1:
        client_obj: Client = clients[0]
        expired_date = client_obj.activated_date + timedelta(days=client_obj.subscribe_duration)
        if expired_date >= date.today():
            await message.answer(xray_url.render())
            await message.answer(f'🔝🔝🔝 Скопируйте ссылку выше 🔝🔝🔝\n\n\n'
                                 f'Ваша подписка действует до {expired_date.strftime("%m.%d.%Y")}\n'
                                 'Для дальнейшей настройки перейдите в "Инструкции" в главном меню и выберите нужную ОС',
                                 reply_markup=support_kb())

        else:
            await message.answer(f'Подписка истекла {expired_date.strftime("%m.%d.%Y")}',
                                 reply_markup=support_kb())

    elif len(clients) > 1:
        await message.answer('На данном номере несколько подписок, свяжитесь с поддержкой',
                             reply_markup=support_kb())
    else:
        await message.answer('Извините, к сожалению не нашлось действующей подписки',
                             reply_markup=support_kb())


async def wrong_number_format(message: Message):
    await message.answer('Неверный формат номера\n'
                         'Введите номер телефона в формате: +70007770077',
                         reply_markup=support_kb())


# todo Стата текущей подписке

# Инструкции
async def os_choose(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер get_instructions')

    await state.clear()
    await call.message.edit_text(text='Выберите операционную систему', reply_markup=os_choose_kb())


async def ios_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер ios_instruction')

    await state.set_state(ChooseOS.OS_SECTION)
    await call.message.edit_text(text='Выберите любую программу', reply_markup=ios_choose_kb())


async def foxray_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер ios_instruction')

    await state.set_state(ChooseOS.PROGRAM_SECTION)
    await call.message.edit_text(text=ios_foxray_instruction.render(), reply_markup=back_kb())


async def streisand_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер ios_instruction')

    await state.set_state(ChooseOS.PROGRAM_SECTION)
    await call.message.edit_text(text=ios_streisand_instruction.render(), reply_markup=back_kb())


async def android_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер android_instruction')

    await state.set_state(ChooseOS.OS_SECTION)
    await call.message.edit_text(text=android_v2ray_instruction.render(), reply_markup=back_kb())


async def windows_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер windows_instruction')

    await state.set_state(ChooseOS.OS_SECTION)
    await call.message.edit_text(text='Windows Картинка', reply_markup=back_kb())


async def linux_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер linux_instruction')

    await state.set_state(ChooseOS.OS_SECTION)
    await call.message.edit_text(text='Linux Guide', reply_markup=back_kb())
