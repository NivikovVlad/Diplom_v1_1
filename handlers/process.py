import os
from aiogram import types
from aiogram.types import callback_query, CallbackQuery

from Database.database import session
import process_photo
from Database.models import User, Referral
from TextForButtons import *
from ClasAndFunc import PhotoState, PhotoDescription, clear, send_photo, return_to_start
from keyboards import *


async def start_command(message: types.Message) -> None:

    if len(message.text.split()) > 1:
        referrer_id = str(message.text.split()[1])
        referrer_user_id = session.query(User.id).filter_by(user_id=referrer_id).first()[0]
        # referrer_user_id = referrer_user_id[0]
    else:
        # referrer_id = None
        referrer_user_id = None

    user_id = str(message.from_user.id)
    username = message.from_user.username
    firstname = message.from_user.first_name

    user = session.query(User).filter_by(user_id=user_id).first()
    if user is None:
        # Пользователь не существует, добавить его в базу данных
        new_user = User(user_id=user_id, username=username, firstname=firstname, referrer_id=referrer_user_id)
        session.add(new_user)
        session.commit()

        if referrer_user_id is not None:
            # Создать новый реферал
            new_referral = Referral(user_id=referrer_user_id, referred_user_id=new_user.id)
            session.add(new_referral)
        session.commit()

    await message.answer(f'Привет {firstname}!\n'
                         f'{start}', reply_markup=start_kb)
    session.close()


async def reload_command(message: types.Message, state):
    user_id = message.from_user.id
    await return_to_start(state, user_id)
    await message.answer(exit_, reply_markup=start_kb)


async def get_profile(message: types.Message):
    user_id = str(message.from_user.id)
    user = session.query(User).filter_by(user_id=user_id).first()
    referrals = session.query(Referral).filter_by(user_id=user.id).all()
    if referrals is None:
        count_ref = 'У вас нет рефералов'
    else:
        count_ref = len(referrals)
    await message.answer(f'ID: {user.user_id}\n'
                         # f'Ник: {user.firstname}\n'
                         f'Баланс: {user.balance} токенов\n'
                         f'Доступно обработок: {user.available_uses} фото\n'
                         f'Всего обработано: {user.total_uses} фото\n'
                         f'Приглашено: {count_ref} пользователей', reply_markup=ref_linc_kb)
    session.close()


async def get_ref(call):
    user_id = str(call.from_user.id)
    await call.message.answer(f'https://t.me/make_loveis_bot?start={user_id}')
    await call.answer()


async def request_photo(message: types.Message):
    await message.answer('🔄 Загрузи фото...')
    await PhotoState.photos.set()


async def print_instruction(message: types.Message):
    await message.answer(instruction, reply_markup=start_kb)


async def get_photos(message: types.Message, album: list[types.Message] = None, state=PhotoState.photos):
    user_id = message.from_user.id
    os.makedirs(f'UserFiles/Photos_{user_id}', exist_ok=True)
    os.makedirs(f'UserFiles/ResultPhotos_{user_id}', exist_ok=True)
    if not album:
        album = [message]

    media_group = types.MediaGroup()
    for file in album:
        if file.photo:
            file_id = file.photo[-1].file_id
        else:
            await message.answer("🆘 Я принимаю только фото!\n"
                                 "Попробуй заново", reply_markup=start_kb)
            # await state.finish()
            await PhotoState.photos.set()
            PhotoDescription.description = []
            clear(user_id)
            return

        try:
            file_path = f'UserFiles/Photos_{user_id}/{file_id}.jpg'
            if os.path.exists(file_path):
                pass
            else:
                await file.photo[-1].download(file_path)
            media_group.attach(types.InputMedia(media=file_id, type=file.content_type))

        except Exception as exc:
            await state.finish()
            PhotoDescription.description = []
            clear(user_id)
            await message.answer(str(exc), reply_markup=card_type_kb)
            return await message.answer("🆘 Что-то пошло не так...", reply_markup=start_kb)

    await message.answer('👌 Фото успешно загружены...')

    await state.update_data(photos=[media_group, user_id])
    await message.answer('🎆 Выбери тип карточки:', reply_markup=card_type_kb)
    await PhotoState.type_card.set()


async def set_type_love_is(call, state):
    await state.update_data(type_card='love_is')
    await call.message.answer('🎆 Выбран тип карточки: "Love is..."', reply_markup=confirm_type_kb)
    await call.answer()
    await PhotoState.descriptions.set()


async def set_type_friend_is(call, state):
    await state.update_data(type_card='friend_is')
    await call.message.answer('🎆 Выбран тип карточки: "Friendship is..."', reply_markup=confirm_type_kb)
    await call.answer()
    await PhotoState.descriptions.set()


async def change_type(message: types.Message, state):
    await state.update_data(type_card='')
    await message.answer('🎆 Выбери тип карточки:', reply_markup=card_type_kb)
    await PhotoState.type_card.set()


async def request_descriptions(message: types.Message, state):
    data = await state.get_data()
    photos = data['photos']

    if photos:
        first_photo = photos[0].media[0]['media']
        # await PhotoState.descriptions.set()
        await send_photo(message, first_photo)
    else:
        await message.answer('🚫 Нет фотографий для обработки.')


async def process_confirmation(message: types.Message, state):
    data = await state.get_data()
    remaining_photos = data.get('photos', [])
    desc = {}

    if len(remaining_photos[0].media) == 1:
        current_photo = remaining_photos[0].media[0]['media']
        current_user_id = remaining_photos[1]
        desc[current_photo] = [message.text, current_user_id]
        PhotoDescription.description.append(desc)

        remaining_photos[0].media.remove(remaining_photos[0].media[0])

        await state.update_data(photos=remaining_photos)
        await message.answer('Фото готовы к обработке', reply_markup=proc_kb)
        await state.update_data(descriptions=PhotoDescription.description)
        await PhotoState.process.set()

    else:
        next_photo = remaining_photos[0].media[1]['media']

        current_photo = remaining_photos[0].media[0]['media']
        current_user_id = remaining_photos[1]
        desc[current_photo] = (message.text, current_user_id)
        PhotoDescription.description.append(desc)

        remaining_photos[0].media.remove(remaining_photos[0].media[0])

        await state.update_data(photos=remaining_photos)
        await send_photo(message, next_photo)


async def get_result_photo(message: types.Message, state):
    user_id = message.from_user.id
    data = await state.get_data()
    photo_descriptions = data['descriptions']
    img_type = data['type_card']
    try:
        for i in range(0, len(photo_descriptions)):
            for photo_id, photo_description in photo_descriptions[i].items():

                if str(photo_description[1]) == str(user_id):
                    process_photo.set_new_image(photo_id, photo_description[0], img_type, user_id)
                    result_photo_path = f'UserFiles/ResultPhotos_{user_id}/{photo_id}.jpg'
                    with open(result_photo_path, 'rb') as photo:
                        await message.answer_photo(photo, caption='📸 Твоя обработанная фотография.')

        await message.answer('✅ Все фотографии успешно обработаны!', reply_markup=start_kb)

    except Exception as exc:
        print(exc)
        await message.answer('🆘 Упс! Что-то сломалось', reply_markup=start_kb)

    finally:
        await return_to_start(state, user_id)
