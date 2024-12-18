from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
# from config import price


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Загрузить фото')],
        [KeyboardButton(text='Инструкция'), KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Перезагрузить')]
    ],
    resize_keyboard=True
)

confirm_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Продолжить')],
        [KeyboardButton(text='Изменить')],
        [KeyboardButton(text='Перезагрузить')]
    ],
    resize_keyboard=True
)

card_type_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Love is...', callback_data='love_is'),
            InlineKeyboardButton(text='Friendship is...', callback_data='friendship_is'),
        ]
    ],
    resize_keyboard=True
)


proc_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Обработать')],
    ],
    resize_keyboard=True
)

ref_linc_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Получить реферальную ссылку', callback_data='get_ref')],
        [InlineKeyboardButton(text='Пополнить баланс', callback_data='buy_token'),]
    ],
    resize_keyboard=True
)

buy_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Купить 500 token', callback_data='confirm_buy'),
        ]
    ],
    resize_keyboard=True
)