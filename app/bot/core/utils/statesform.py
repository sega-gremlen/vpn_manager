from aiogram.fsm.state import StatesGroup, State


class BuySubSteps(StatesGroup):
    GET_PERIODS = State()
    PAY_SUB = State()


class CheckExistingSub(StatesGroup):
    GET_NUMBER = State()
    CHOOSE_NUMBER = State()


class ChooseOS(StatesGroup):
    OS_SECTION = State()
    PROGRAM_SECTION = State()

