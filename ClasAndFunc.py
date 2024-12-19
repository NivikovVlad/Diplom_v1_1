from __future__ import annotations

import asyncio
import os

from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


async def return_to_start(state, user_id):
    """
    Сброс состояний и возврат к началу
    """
    await state.finish()
    PhotoDescription.description = []
    clear(user_id)


def clear(user_id):
    """
    Очистка директорий пользователя после обработки фото
    """
    photo_list_ish = os.listdir(f'UserFiles/Photos_{user_id}')
    photo_list_fin = os.listdir(f'UserFiles/ResultPhotos_{user_id}')

    for photo in photo_list_ish:
        os.remove(f'UserFiles/Photos_{user_id}/{photo}')
    for photo in photo_list_fin:
        os.remove(f'UserFiles/ResultPhotos_{user_id}/{photo}')


class PhotoDescription:
    """
    Список для хранения фото, подписи и id пользователя
    """
    description = []


class PhotoState(StatesGroup):
    """
    Состояния по которым бот последовательно запрашивает и обрабатывает данные
    """
    waiting_for_description_check = State()
    waiting_for_description = State()
    photos = State()
    type_card = State()
    descriptions = State()
    process = State()
    last = State()


class AlbumMiddleware(BaseMiddleware):
    """
    Прослойка для перехвата обработчика сообщений.
    Если обнаруживает параметр media_group_id, то есть если пользователем было отправлено несколько файлов,
    формирует альбом.
    Мидлварь необходима для обработки нескольких файлов как одно сообщение,
    иначе каждый файл будет считаться отдельным сообщением
    """
    album_data: dict = {}

    def __init__(self, latency: int | float = 0.3):
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        Если media_group_id не обнаружен - отдает управление хендлерам бота
        """
        if not message.media_group_id:
            return

        try:
            # Добавляем в альбом сообщение(в данном случае каждое фото)
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """
        Когда получено последнее сообщение - очищает album_data
        """
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]
        else:
            return


async def send_photo(message: types.Message, photo: str):
    """
    Принимает фото и бот печатает его пользователю с предложением написать подпись.
    Устанавливаем состояние waiting_for_description
    :param message: Продолжить, нужен для получения user_id
    :param photo: id фото
    """
    user_id = message.from_user.id
    await PhotoState.waiting_for_description.set()
    file_path = f'UserFiles/Photos_{user_id}/{photo}.jpg'
    with open(file_path, 'rb') as img:
        await message.answer_photo(img, caption='✍ Напиши подпись для этого фото')\
