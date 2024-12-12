from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Загрузить фото')],
        [KeyboardButton(text='Инструкция')]
    ],
    resize_keyboard=True
)

next_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Продолжить')],
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