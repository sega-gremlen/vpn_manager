from aiogram.filters.callback_data import CallbackData

# class


class MainMenu(CallbackData, prefix='main_menu'):
    buy_sub: str
    exist_sub: str
    my_sub: str
    instructions: str
    support: str
