from aiogram.fsm.state import StatesGroup, State


class BuySubSteps(StatesGroup):
    GET_PERIODS = State()
    PAY_SUB = State()
    TRIAL = State()
    GET_NOTI_SUCCESS = State()
    SUB_ACTIVATED = State()

class MyProfile(StatesGroup):
    GET_INSIDE = State()
    GET_URL = State()

class Instructions(StatesGroup):
    OS_SECTION = State()
    PROGRAM_SECTION = State()
    IOS_SECTION = State()
    MACOS_SECTION = State()
    ANDROID_SECTION = State()
    WINDOWS_SECTION = State()
    LINUX_SECTION = State()

class Admin(StatesGroup):
    REFUND_SUB = State()
    GET_CONF_URL = State()
    ADD_USER = State()



