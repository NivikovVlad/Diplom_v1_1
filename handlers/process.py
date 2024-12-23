import os
from aiogram import types

from Database.database import session
import process_photo
from Database.models import User, Referral
from TextForButtons import *
from ClasAndFunc import PhotoState, PhotoDescription, clear, send_photo, return_to_start
from keyboards import *


async def start_command(message: types.Message):
    """
    Обработчик для команды /start. Добавляет пользователя в БД.
    Начисляет вознаграждение за реферала
    """
    if len(message.text.split()) > 1:
        # Получаем id пользователя телеграмм, по чьей ссылке мы перешли
        referrer_user_id = str(message.text.split()[1])
        # Получаем id этого пользователя в БД
        referrer_bd_id = session.query(User.id).filter_by(user_id=referrer_user_id).first()[0]
    else:
        referrer_user_id = None
        referrer_bd_id = None

    user_id = str(message.from_user.id)
    username = message.from_user.username
    firstname = message.from_user.first_name

    # Проверяем есть ли пользователь в БД
    user = session.query(User).filter_by(user_id=user_id).first()
    if user is None:
        # Пользователь не существует, добавить его в базу данных
        new_user = User(user_id=user_id, username=username, firstname=firstname)
        session.add(new_user)
        session.commit()

        # Если пользователь пришел по реферальной ссылке
        if referrer_user_id is not None:
            # Добавить запись в таблицу рефералов
            new_referral = Referral(user_id=new_user.id, referrer_id=referrer_bd_id)
            session.add(new_referral)
            # Начислить пригласившему бонус
            session.query(User).filter_by(id=referrer_bd_id).update({User.balance: User.balance + 50})

        session.commit()

    await message.answer(f'Привет {firstname}!\n'
                         f'{start}', reply_markup=start_kb)
    session.close()


async def request_photo(message: types.Message):
    """
    Бот запрашивает фото
    """
    user_id = str(message.from_user.id)
    # Проверяем баланс пользователя, чтобы узнать сколько обработок ему доступно
    balance = session.query(User.balance).filter_by(user_id=user_id).first()[0]
    await message.answer('🔄 Загрузи фото...\n'
                         f'Для обработки доступно {balance // 10} фото')
    session.close()
    await PhotoState.photos.set()


async def get_photos(message: types.Message, album: list[types.Message] = None, state=PhotoState.photos):
    """
    Бот получает фото, сохраняет их.
    :param album: Мидлварь формирует альбом из присланных фото
    :param state: Обработчик срабатывает в состоянии photos
    """

    # Создаем директории под конкретного пользователя
    user_id = message.from_user.id
    os.makedirs(f'UserFiles/Photos_{user_id}', exist_ok=True)
    os.makedirs(f'UserFiles/ResultPhotos_{user_id}', exist_ok=True)
    if not album:
        album = [message]   # Если фото одно, то альбом состоит из сообщения пользователя

    media_group = types.MediaGroup()    # Формируем медиа-группу
    user_id = str(message.from_user.id)
    balance = session.query(User.balance).filter_by(user_id=user_id).first()[0]
    session.close()

    # Проверяем доступно ли пользователю обработка стольких фото
    if len(album) <= balance / 10:
        for file in album:
            # Если, в альбоме попадается не фото, возвращаем на предыдущее состояние,
            # иначе получаем id фото
            if file.photo:
                file_id = file.photo[-1].file_id
            else:
                await message.answer("🆘 Я принимаю только фото!\n"
                                     "Попробуй заново", reply_markup=start_kb)

                await PhotoState.photos.set()
                PhotoDescription.description = []
                clear(user_id)
                return

            try:
                # Сохраняем фото на сервер
                file_path = f'UserFiles/Photos_{user_id}/{file_id}.jpg'
                if os.path.exists(file_path):
                    pass
                else:
                    await file.photo[-1].download(file_path)
                # Добавляем фото в медиа-группу
                media_group.attach(types.InputMedia(media=file_id, type=file.content_type))

            except Exception as exc:
                session.close()
                await state.finish()
                PhotoDescription.description = []
                clear(user_id)
                await message.answer(str(exc), reply_markup=card_type_kb)
                return await message.answer("🆘 Что-то пошло не так...", reply_markup=start_kb)
    else:
        # session.close()
        await state.finish()
        PhotoDescription.description = []
        clear(user_id)
        return await message.answer(f"🆘 Вам доступно {balance // 10} фото\n"
                                    f"  Вы загрузили {len(album)} фото", reply_markup=start_kb)

    await message.answer('👌 Фото успешно загружены...')

    await state.update_data(photos=[media_group, user_id])
    await message.answer('🎆 Выбери тип карточки:', reply_markup=card_type_kb)
    await PhotoState.type_card.set()


async def set_type_love_is(call, state):
    """
    Устанавливаем тип карточки в хранилище состояния
    """
    await state.update_data(type_card='love_is')
    await call.message.answer('🎆 Выбран тип карточки: "Love is..."', reply_markup=confirm_type_kb)
    await call.answer()
    await PhotoState.descriptions.set()


async def set_type_friend_is(call, state):
    """
    Устанавливаем тип карточки в хранилище состояния
    """
    await state.update_data(type_card='friend_is')
    await call.message.answer('🎆 Выбран тип карточки: "Friendship is..."', reply_markup=confirm_type_kb)
    await call.answer()
    await PhotoState.descriptions.set()


async def change_type(message: types.Message, state):
    """
    Позволяет изменить тип карточки
    """
    await state.update_data(type_card='')
    await message.answer('🎆 Выбери тип карточки:', reply_markup=card_type_kb)
    await PhotoState.type_card.set()


async def request_descriptions(message: types.Message, state):
    """
    Инициализируем запрос подписи к фото.
    :param message Продолжить с клавиатуры
    """
    data = await state.get_data()
    # Список фоток
    photos = data['photos']

    if photos:
        # Берем первое фото и передаем его в send_photo
        first_photo = photos[0].media[0]['media']
        await send_photo(message, first_photo)
    else:
        await message.answer('🚫 Нет фотографий для обработки.')


async def process_confirmation(message: types.Message, state):
    """
    Срабатывает в состоянии waiting_for_description.
    Отправляет фото на подпись пользователю.
    Формируем словарь desc.
    Добавляем словарь desc в список PhotoDescription.description
    PhotoDescription.description - список всех фото с подписями и привязкой к id пользователя
    """
    data = await state.get_data()
    remaining_photos = data.get('photos', [])   # Список оставшихся фото
    desc = {}   # Словарь. Ключ - id фото, значение - список[подпись, id пользователя]

    # Если фото последнее или изначально одно
    if len(remaining_photos[0].media) == 1:
        current_photo = remaining_photos[0].media[0]['media']
        current_user_id = remaining_photos[1]
        desc[current_photo] = [message.text, current_user_id]
        PhotoDescription.description.append(desc)   # Список словарей desc

        # После добавления в словарь, удаляем фото
        remaining_photos[0].media.remove(remaining_photos[0].media[0])

        # Обновляем состояние на текущее количество фото
        await state.update_data(photos=remaining_photos)
        await message.answer('Фото готовы к обработке', reply_markup=proc_kb)
        # Заносим собранные данные по всем фото в состояние descriptions
        await state.update_data(descriptions=PhotoDescription.description)
        await PhotoState.process.set()

    else:
        # Определяем следующее фото для отправки на подпись
        next_photo = remaining_photos[0].media[1]['media']

        # Определяем текущее фото и записываем его вместе с подписью и id пользователя
        current_photo = remaining_photos[0].media[0]['media']
        current_user_id = remaining_photos[1]
        desc[current_photo] = (message.text, current_user_id)
        PhotoDescription.description.append(desc)

        # Удаляем текущее фото из списка
        remaining_photos[0].media.remove(remaining_photos[0].media[0])
        # Обновляем состояние на текущее количество фото
        await state.update_data(photos=remaining_photos)
        # Передаем следующее фото для запроса подписи
        await send_photo(message, next_photo)


async def get_result_photo(message: types.Message, state):
    user_id = message.from_user.id
    data = await state.get_data()
    photo_descriptions = data['descriptions']
    img_type = data['type_card']
    try:
        # Распаковка состояния descriptions (id фото, подпись, id пользователя)
        for i in range(0, len(photo_descriptions)):
            for photo_id, photo_description in photo_descriptions[i].items():
                if str(photo_description[1]) == str(user_id):
                    # Отправляем фото и остальные данные на формирование итогового результата
                    process_photo.set_new_image(photo_id, photo_description[0], img_type, user_id)
                    result_photo_path = f'UserFiles/ResultPhotos_{user_id}/{photo_id}.jpg'
                    # Отправляем пользователю результат обработки фото
                    # with open(result_photo_path, 'rb') as photo:
                    #     await message.answer_photo(photo, caption='📸 Твоя обработанная фотография.')

        # Снимаем с баланса поинты за обработанные фото
        session.query(User).filter_by(user_id=str(user_id)).update(
            {User.balance: User.balance - len(photo_descriptions) * 10})
        # Счетчик обработанных фото
        session.query(User).filter_by(user_id=str(user_id)).update(
            {User.total_uses: User.total_uses + len(photo_descriptions)})
        session.commit()
        session.close()

        # Получим путь к pdf
        path_to_pdf_file = process_photo.get_pdf(user_id)
        await message.answer('✅ Все фотографии успешно обработаны!')
        with open(path_to_pdf_file, 'rb') as file:
            await message.answer_document(file, caption='📑 Осталось только распечатать')

    except Exception as exc:
        print(exc)
        await message.answer('🆘 Упс! Что-то сломалось', reply_markup=start_kb)

    finally:
        await return_to_start(state, user_id)
