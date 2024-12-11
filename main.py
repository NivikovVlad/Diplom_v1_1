from __future__ import annotations
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

import About_goods
import process_photo
from keyboards import *
from About_goods import *
from ClasAndFunc import PhotoDescription, PhotoState, AlbumMiddleware, clear


load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(start, reply_markup=start_kb)


@dp.message_handler(text=['Загрузить фото'], state='*')
async def request_photo(message: types.Message):
    await message.answer('🔄 Загрузи фото...')
    await PhotoState.photos.set()


@dp.message_handler(text=['Инструкция'])
async def set_instruction(message: types.Message):
    await message.answer(instruction, reply_markup=start_kb)


@dp.message_handler(content_types=types.ContentType.ANY, state=PhotoState.photos)
async def get_message(message: types.Message, album: list[types.Message] = None, state=None):
    if not album:
        album = [message]

    media_group = types.MediaGroup()
    for file in album:
        if file.photo:
            file_id = file.photo[-1].file_id
        else:
            continue

        try:
            file_path = f'UserFiles/Photos/{file_id}.jpg'
            if os.path.exists(file_path):
                pass
            else:
                await file.photo[-1].download(file_path)
            media_group.attach(types.InputMedia(media=file_id, type=file.content_type))

        except ValueError:
            return await message.answer("🆘 Что-то пошло не так...")

    await message.answer('👌 Фото успешно загружены...')

    await state.update_data(photos=media_group)
    await message.answer('🎆 Выбери тип карточки:', reply_markup=card_type_kb)
    await PhotoState.type_card.set()


@dp.callback_query_handler(text=['love_is'], state=PhotoState.type_card)
async def set_type_love_is(call, state):
    await state.update_data(type_card='love_is')
    await call.message.answer('🎆 Выбран тип карточки: "Love is..."', reply_markup=next_kb)
    await PhotoState.descriptions.set()


@dp.callback_query_handler(text=['friend_is'], state=PhotoState.type_card)
async def set_type_friend_is(call, state):
    await state.update_data(type_card='friend_is')
    await call.message.answer('🎆 Выбран тип карточки: "Friend is..."', reply_markup=next_kb)
    await PhotoState.descriptions.set()


@dp.message_handler(text=['Продолжить'], state=PhotoState.descriptions)
async def request_descriptions(message: types.Message, state):

    data = await state.get_data()
    photos = data['photos']

    if photos:
        first_photo = photos.media[0]['media']
        await PhotoState.descriptions.set()
        await send_photo(message, state, first_photo)
    else:
        await message.answer('🚫 Нет фотографий для обработки.')


async def send_photo(message: types.Message, state, photo: str):

    await PhotoState.waiting_for_description.set()
    file_path = f'UserFiles/Photos/{photo}.jpg'
    with open(file_path, 'rb') as img:
        await message.answer_photo(img, caption='✍ Напиши подпись для этого фото')


@dp.message_handler(state=PhotoState.waiting_for_description)
async def process_confirmation(message: types.Message, state):

    data = await state.get_data()
    remaining_photos = data.get('photos', [])
    desc = {}

    if len(remaining_photos.media) == 1:
        current_photo = remaining_photos.media[0]['media']
        desc[current_photo] = message.text
        PhotoDescription.description.append(desc)

        remaining_photos.media.remove(remaining_photos.media[0])

        await state.update_data(photos=remaining_photos)
        await message.answer('Фото готовы к обработке', reply_markup=proc_kb)
        await state.update_data(descriptions=PhotoDescription.description)
        await PhotoState.process.set()

    else:
        next_photo = remaining_photos.media[1]['media']

        current_photo = remaining_photos.media[0]['media']
        desc[current_photo] = message.text
        PhotoDescription.description.append(desc)

        remaining_photos.media.remove(remaining_photos.media[0])

        await state.update_data(photos=remaining_photos)
        await send_photo(message, state, next_photo)


@dp.message_handler(text=['Обработать'], state=PhotoState.process)
async def check(message: types.Message, state):
    data = await state.get_data()
    photo_descriptions = data['descriptions']
    img_type = data['type_card']
    try:
        for i in range(0, len(photo_descriptions)):
            for photo_id, photo_description in photo_descriptions[i].items():
                process_photo.set_new_image(photo_id, photo_description, img_type)

                result_photo_path = f'UserFiles/ResultPhotos/{photo_id}.jpg'
                with open(result_photo_path, 'rb') as photo:
                    await message.answer_photo(photo, caption='📸 Твоя обработанная фотография.')

        clear()
        await state.finish()
        await message.answer('✅ Все фотографии успешно обработаны!', reply_markup=start_kb)

        # await state.reset()
        PhotoDescription.description = []

    except Exception as exc:
        print(exc)
        await state.finish()
        # await state.reset()
        PhotoDescription.description = []
        clear()
        await message.answer('🆘 Упс! Что-то сломалось', reply_markup=start_kb)


if __name__ == '__main__':
    os.makedirs('UserFiles/Photos', exist_ok=True)
    os.makedirs('UserFiles/ResultPhotos', exist_ok=True)
    album_middleware = AlbumMiddleware()
    dp.middleware.setup(album_middleware)
    executor.start_polling(dp, skip_updates=True)
