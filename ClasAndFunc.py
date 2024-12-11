from __future__ import annotations

import asyncio
import os

from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


def clear(user_id):
    photo_list_ish = os.listdir(f'UserFiles/Photos_{user_id}')
    photo_list_fin = os.listdir(f'UserFiles/ResultPhotos_{user_id}')

    for photo in photo_list_ish:
        os.remove(f'UserFiles/Photos_{user_id}/{photo}')
    for photo in photo_list_fin:
        os.remove(f'UserFiles/ResultPhotos_{user_id}/{photo}')


class PhotoDescription:
    description = []


class PhotoState(StatesGroup):
    waiting_for_description_check = State()
    waiting_for_description = State()
    photos = State()
    type_card = State()
    descriptions = State()
    process = State()
    last = State()


class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: int | float = 0.3):
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]
        else:
            return
