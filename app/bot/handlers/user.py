from datetime import timedelta, datetime

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from app.bot.utils.statesform import BuySubSteps, Instructions, MyProfile
from aiogram.fsm.context import FSMContext

from app.bot.keyboards.inline import *
from app.bot.utils.jinja_templates import *
from app.db.payment_requests.models import PaymentRequests
from app.db.subscriptions.dao import SubscriptionsDAO
from app.db.subscriptions.models import Subscriptions
from app.db.users.dao import UsersDAO, Users
from app.db.subscription_types.dao import SubscriptionTypesDAO
from app.main_interface import main_interface


# -------------------- Оформление новой подписки --------------------
async def get_main_menu(message: Message, state: FSMContext):
    print('Запущен хэндлер get_main_menu')
    await state.clear()
    if type(message) is CallbackQuery:
        await message.message.edit_text(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())
    else:
        if message.text.startswith('/'):
            await main_interface.create_user(telegram_id=message.from_user.id)
            return await message.answer(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())
        else:
            try:
                await message.edit_text(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())
            except TelegramBadRequest:
                await message.answer(text=user_main_menu_tm.render(), reply_markup=user_main_menu_kb())


async def buy_subscription(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер buy_subscription')
    await state.update_data(user_id=call.message.from_user.id)
    await state.set_state(BuySubSteps.GET_PERIODS)
    await call.answer()
    # Находим актуальные планы подписок
    sub_prices = await SubscriptionTypesDAO().find_all_by_filter()
    sub_prices = [(i['name'], i['price'], i['duration']) for i in sub_prices]
    user: Users = await UsersDAO.find_one_or_none(telegram_id=call.from_user.id)
    return await call.message.edit_text(buy_subscription_tm,
                                 reply_markup=periods_value_kb(sub_prices,
                                                               user.trial_wasted))


async def buy_subscription_get_periods(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер buy_subscription_get_periods')
    await call.answer()
    sub_type = await SubscriptionTypesDAO.find_one_or_none(name=call.data)
    telegram_id = call.from_user.id
    dt_now = datetime.now()

    if sub_type.name == 'trial':
        await state.set_state(BuySubSteps.TRIAL)
        stop_date = dt_now + timedelta(sub_type.duration)
        return await call.message.edit_text(
            text=sub_activity_info.render({'stop_date': stop_date.strftime("%d.%m.%Y %H:%M:%S")}),
            reply_markup=activate_trial_kb())
    else:
        # Проверка длительности будущей подписки
        last_sub: Subscriptions = await SubscriptionsDAO.find_last_sub_by_user_tg_id(telegram_id)
        if last_sub and last_sub.stop >= dt_now and last_sub.subscription_type_id != 4:
            stop_date = (last_sub.stop + timedelta(sub_type.duration))
        else:
            stop_date = dt_now + timedelta(sub_type.duration)

        payment_request: PaymentRequests = await main_interface.create_payment_request(
            telegram_id,
            sub_type,
        )
        redirect_url = await main_interface.create_redirect_url(payment_request.label)
        await state.set_state(BuySubSteps.PAY_SUB)
        return await call.message.edit_text(
            text=sub_activity_info.render({'stop_date': stop_date.strftime("%d.%m.%Y %H:%M:%S")}),
            reply_markup=pay_kb(sub_type, redirect_url))


async def activate_trial(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер activate_trial')
    await state.set_state(BuySubSteps.SUB_ACTIVATED)
    await call.answer()
    raw_xray_url = await main_interface.activate_trial_subscription(call.from_user.id)
    return await call.message.answer(text=xray_url.render(raw_xray_url) + '\n' + first_sub_activated_msg,
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=main_menu())


async def wait_for_payment(call: CallbackQuery):
    print('Запущен хэндлер wait_for_payment')
    return await call.message.answer('Ждём подтверждения оплаты...')

# -------------------- Статистика подписки --------------------
async def my_profile(call: CallbackQuery, state: FSMContext):
    await state.set_state(MyProfile.GET_INSIDE)
    telegram_id = call.from_user.id
    if await main_interface.get_active_subscription(telegram_id):
        user_stat = await main_interface.get_user_stat(telegram_id)
        await call.message.edit_text(text=profile_stat.render(user_stat),
                                     reply_markup=profile_stat_kb())
    else:
        await call.message.edit_text(text=profile_stat_unsub.render({'telegram_id':telegram_id}),
                                     reply_markup=back_kb())


async def show_url_conf(call: CallbackQuery, state: FSMContext):
    await state.set_state(MyProfile.GET_URL)
    user: Users = await UsersDAO.find_one_or_none(telegram_id=call.from_user.id)
    conf_url = await main_interface.render_xray_url(user.xray_uuid)
    await call.message.edit_text(text=xray_url.render(conf_url),
                                 parse_mode=ParseMode.HTML,
                                 reply_markup=back_kb())

# -------------------- Инструкции --------------------
async def os_choose(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер os_choose')
    await state.clear()
    await call.message.edit_text(text='Выберите операционную систему', reply_markup=os_choose_kb())


async def ios_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер ios_instruction')
    await state.set_state(Instructions.OS_SECTION)
    await call.message.edit_text(text='Выберите любую программу', reply_markup=ios_choose_kb())


async def macos_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер macos_instruction')
    await state.set_state(Instructions.OS_SECTION)
    await call.message.edit_text(text='Выберите любую программу', reply_markup=macos_choose_kb())


async def android_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер android_instruction')
    await state.set_state(Instructions.OS_SECTION)
    await call.message.edit_text(text='Выберите любую программу', reply_markup=android_choose_kb())


async def windows_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер windows_instruction')
    await state.set_state(Instructions.OS_SECTION)
    await call.message.edit_text(text='Выберите любую программу', reply_markup=windows_choose_kb())


async def linux_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер linux_instruction')
    await state.set_state(Instructions.OS_SECTION)
    await call.message.edit_text(text='Выберите любую программу', reply_markup=linux_choose_kb())


async def ios_foxray_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер foxray_instruction')
    await state.set_state(Instructions.IOS_SECTION)
    await call.message.edit_text(text=ios_foxray_instruction_tm, reply_markup=back_kb())


async def ios_streisand_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер streisand_instruction')
    await state.set_state(Instructions.IOS_SECTION)
    await call.message.edit_text(text=ios_streisand_instruction_tm,
                                 reply_markup=back_kb(),
                                 parse_mode=ParseMode.HTML)


async def ios_v2box_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер streisand_instruction')
    await state.set_state(Instructions.IOS_SECTION)
    await call.message.edit_text(text=ios_v2box_instruction_tm,
                                 reply_markup=back_kb(),
                                 parse_mode=ParseMode.HTML)


async def macos_nekoray_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер streisand_instruction')
    download_url_intel = await main_interface.get_latest_github_release('macos_nekoray_intel')
    download_url_apple = await main_interface.get_latest_github_release('macos_nekoray_apple')
    await state.set_state(Instructions.MACOS_SECTION)
    await call.message.edit_text(text=macos_nekoray_instruction_tm,
                                 reply_markup=download_macos_nekoray(download_url_intel,
                                                                     download_url_apple),
                                 parse_mode=ParseMode.HTML)


async def macos_v2box_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер streisand_instruction')
    await state.set_state(Instructions.MACOS_SECTION)
    await call.message.edit_text(text=macos_v2box_instruction_tm,
                                 reply_markup=back_kb(),
                                 parse_mode=ParseMode.HTML)


async def android_nekobox_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер android_nekobox_instruction')
    download_url = await main_interface.get_latest_github_release('android_nekobox')
    await state.set_state(Instructions.ANDROID_SECTION)
    await call.message.edit_text(text=android_nekobox_instruction_tm,
                                 reply_markup=download_android_nekobox(download_url),
                                 parse_mode=ParseMode.HTML)


async def android_v2rayng_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер android_v2ray_instruction')
    download_url = await main_interface.get_latest_github_release('android_v2rayNG')
    await state.set_state(Instructions.ANDROID_SECTION)
    await call.message.edit_text(text=android_v2ray_instruction_tm.render(),
                                 reply_markup=download_android_v2rayNG(download_url),
                                 parse_mode=ParseMode.HTML)


async def windows_invisible_man_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер windows_xray_instruction')
    download_url = await main_interface.get_latest_github_release('windows_invisible_man')
    await state.set_state(Instructions.WINDOWS_SECTION)
    await call.message.edit_text(text=windows_invisible_man_instruction_tm,
                                 reply_markup=download_windows_invisible_man(download_url),
                                 parse_mode=ParseMode.HTML)


async def windows_nekoray_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер windows_nekoray_instruction')
    download_url = await main_interface.get_latest_github_release('windows_nekoray')
    await state.set_state(Instructions.WINDOWS_SECTION)
    await call.message.edit_text(text=windows_nekoray_instruction_tm,
                                 reply_markup=download_windows_nekoray(download_url),
                                 parse_mode=ParseMode.HTML)


async def linux_nekoray_instruction(call: CallbackQuery, state: FSMContext):
    print('Запущен хэндлер windows_nekoray_instruction')
    await state.set_state(Instructions.WINDOWS_SECTION)
    await call.message.edit_text(text=linux_nekoray_instruction_tm,
                                 reply_markup=back_kb(),
                                 parse_mode=ParseMode.HTML)
