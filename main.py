from __future__ import annotations
from config import token
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from ClasAndFunc import AlbumMiddleware
from handlers.process import *
from handlers.users import *

bot = Bot(token)
dp = Dispatcher(bot, storage=MemoryStorage())


dp.message_handler(commands=['start'])(start_command)
dp.message_handler(text=['Перезагрузить'], state='*')(reload_command)
dp.message_handler(text=['Профиль'])(get_profile)
dp.callback_query_handler(text=['get_ref'])(get_ref)
dp.callback_query_handler(text=['buy_token'])(buy_token)
dp.callback_query_handler(text=['confirm_buy'])(confirm_buy)
dp.message_handler(text=['Загрузить фото'], state='*')(request_photo)
dp.message_handler(text=['Инструкция'])(print_instruction)

dp.message_handler(content_types=types.ContentType.ANY, state=PhotoState.photos)(get_photos)

dp.callback_query_handler(text=['love_is'], state=PhotoState.type_card)(set_type_love_is)
dp.callback_query_handler(text=['friendship_is'], state=PhotoState.type_card)(set_type_friend_is)
dp.message_handler(text=['Изменить'], state=PhotoState.descriptions)(change_type)
dp.message_handler(text=['Продолжить'], state=PhotoState.descriptions)(request_descriptions)

dp.message_handler(state=PhotoState.waiting_for_description)(process_confirmation)
dp.message_handler(text=['Обработать'], state=PhotoState.process)(get_result_photo)


if __name__ == '__main__':
    os.makedirs('UserFiles', exist_ok=True)
    album_middleware = AlbumMiddleware()
    dp.middleware.setup(album_middleware)
    executor.start_polling(dp, skip_updates=True)
