from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


new_order_btn = KeyboardButton('/new_order')

greet_kb1 = ReplyKeyboardMarkup(resize_keyboard=True,).add(new_order_btn)

inline_kb1 = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Изменить кол-во',
                                 callback_data='count'),
            InlineKeyboardButton(text='Указть цену',
                                 callback_data='price'),
        ],
        [
            InlineKeyboardButton(text='Продолжить ✅',
                                 callback_data='continue'),
        ],
    ]
)

inline_finalize = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Добавить товары',
                                 callback_data='add'),
        ],
        [
            InlineKeyboardButton(text='Сформировать КП ✅',
                                 callback_data='create'),
        ],
    ]
)

pdf = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='В PDF ✅',
                                 callback_data='convert'),
        ],
    ]
)
