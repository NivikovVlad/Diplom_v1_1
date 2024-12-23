from aiogram import types

from Database.database import session
from Database.models import User, Referral
from TextForButtons import *
from ClasAndFunc import return_to_start
from config import admin
from keyboards import *


async def print_instruction(message: types.Message):
    """
    Инструкция по использованию бота
    """
    await message.answer(instruction, reply_markup=start_kb)


async def reload_command(message: types.Message, state):
    """
    Инициализирует сброс состояний и возврат к началу для пользователя
    """
    user_id = message.from_user.id
    await return_to_start(state, user_id)
    await message.answer(exit_, reply_markup=start_kb)


async def get_profile(message: types.Message):
    """
    Бот печатает пользователю данные профиля
    """
    user_id = str(message.from_user.id)
    user = session.query(User).filter_by(user_id=user_id).first()
    referrals = session.query(Referral).filter_by(referrer_id=user.id).all()

    # Количество приглашенных пользователей
    if referrals is None:
        count_ref = 'У вас нет рефералов'
    else:
        count_ref = len(referrals)

    # Для админа доступна доп информация
    if user.user_id == admin:
        # Для админа - самый богатый пользователь
        richer = session.query(User).order_by(User.balance.desc()).first()
        dop_info = f'Богатей! ID: {richer.user_id}, баланс: {richer.balance}'
    else:
        # Для юзверя - кто его пригласил
        referer_id = session.query(Referral.referrer_id).filter_by(user_id=user.id).first()[0]
        referer = session.query(User.user_id).filter_by(id=referer_id).first()[0]
        dop_info = f'Вас пригласил: {referer}'

    await message.answer(f'Ник: {user.firstname}\n'
                         f'Баланс: {user.balance} токенов\n'
                         f'Доступно обработок: {user.balance // 10} фото\n'
                         f'Всего обработано: {user.total_uses} фото\n'
                         f'Приглашено: {count_ref} пользователей\n'
                         f'{dop_info}',
                         reply_markup=ref_linc_kb)
    session.close()


async def get_ref(call):
    """
    Получение реф ссылки
    """
    user_id = str(call.from_user.id)
    await call.message.answer(f'https://t.me/make_loveis_bot?start={user_id}')
    await call.answer()


async def buy_token(call):
    """
    Инициализация покупки токенов. Beta
    """
    await call.message.answer('10 token = 1 фото. 1 token = 1 unit', reply_markup=buy_kb)
    await call.answer()


async def confirm_buy(call):
    """
    Beta
    Покупка токенов. Пока заглушка. Просто начисляет 500 токенов
    """
    try:
        user_id = str(call.from_user.id)
        session.query(User).filter_by(user_id=user_id).update({User.balance: User.balance + 500})
        session.commit()
        session.close()
        await call.message.answer('Успешная покупка!', reply_markup=start_kb)
        await call.answer()
    except:
        session.close()