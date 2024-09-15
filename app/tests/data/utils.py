from datetime import datetime, timedelta
import random

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import User, Chat, Message, CallbackQuery, Update

dt_now = datetime.now()

user_1_tg = 1000000000
user_2_tg = 2000000000
user_3_tg = 3000000000
user_4_tg = 4000000000
user_5_tg = 5000000000

sub_1_start = dt_now - timedelta(days=48)
sub_2_start = dt_now - timedelta(days=85)
sub_3_start = dt_now - timedelta(days=10)
sub_4_start = dt_now - timedelta(days=145)


def get_message(text: str, tg_user_id=None, chat_id=None):
    return Message(
        message_id=random.randint(1, 100000000),
        date=datetime.now(),
        chat=Chat(id=chat_id, type='private', user_id=tg_user_id),
        from_user=User(id=tg_user_id, is_bot=False, first_name='TEST_TG_USER'),
        sender_chat=Chat(id=chat_id, type='private', user_id=tg_user_id),
        text=text
    )


def get_callback_querry(data: str, tg_user_id=None, chat_id=None):
    return CallbackQuery(
        id =str(random.randint(0, 10000000)),
        from_user=User(id=tg_user_id, is_bot=False, first_name='TEST_TG_USER'),
        chat_instance=str(random.randint(0, 10000000)),
        data=data,
        message=get_message('asd', tg_user_id, chat_id),
    )


def get_update(message: Message = None, call: CallbackQuery = None, edited_message: Message = None):
    return Update(update_id=random.randint(0, 10000000),
                  message=message if message else None,
                  callback_query=call if call else None,
                  edited_message=edited_message if edited_message else None,)

def get_state(user_chat_id, user_tg_id, bot, memory_storage):
    storage_key = StorageKey(chat_id=user_chat_id, user_id=user_tg_id, bot_id=bot.id)
    state = FSMContext(
        storage=memory_storage,
        key=storage_key
    )
    return state


if '__main__' == __name__:
    print(get_message('asd'))
